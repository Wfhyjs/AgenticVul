# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import torch
import torch.nn as nn
import torch
from torch.autograd import Variable
import copy
import torch.nn.functional as F
from torch.nn import CrossEntropyLoss, MSELoss
import importlib.util

# module_name = 'modelGNN_updates'
# file_path = 'modelGNN_updates.py'
#
# spec = importlib.util.spec_from_file_location(module_name, file_path)
# module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(module)
#
# module_name1 = 'utils'
# file_path1 = 'utils.py'
#
# spec1 = importlib.util.spec_from_file_location(module_name1, file_path1)
# module1 = importlib.util.module_from_spec(spec1)
# spec1.loader.exec_module(module1)
# # 现在可以使用 module 中的函数和类
from .modelGNN_updates import *
from .utils import *

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Model(nn.Module):
    def __init__(self, encoder, config, tokenizer, args):
        super(Model, self).__init__()
        self.encoder = encoder
        self.config = config
        self.tokenizer = tokenizer
        self.args = args

    def forward(self, input_ids=None, labels=None):
        outputs = self.encoder(input_ids, attention_mask=input_ids.ne(1))[0]
        logits = outputs
        prob = F.sigmoid(logits)
        if labels is not None:
            labels = labels.float()
            loss = torch.log(prob[:, 0] + 1e-10) * labels + torch.log((1 - prob)[:, 0] + 1e-10) * (1 - labels)
            loss = -loss.mean()
            return loss, prob
        else:
            return prob


class PredictionClassification(nn.Module):
    """Head for sentence-level classification tasks."""

    def __init__(self, config, args, input_size=None):
        super().__init__()
        # self.dense = nn.Linear(args.hidden_size * 2, args.hidden_size)
        if input_size is None:
            input_size = args.hidden_size
        self.dense = nn.Linear(input_size, args.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.out_proj = nn.Linear(args.hidden_size, args.num_classes)

    def forward(self, features):  #
        x = features
        x = self.dropout(x)
        x = self.dense(x.float())
        x = torch.tanh(x)
        x = self.dropout(x)
        x = self.out_proj(x)
        return x


class GNNReGVD(nn.Module):
    def __init__(self, encoder, config, tokenizer, args):
        super(GNNReGVD, self).__init__()
        self.encoder = encoder
        self.config = config
        self.tokenizer = tokenizer
        self.args = args

        self.w_embeddings = self.encoder.roberta.embeddings.word_embeddings.weight.data.cpu().detach().clone().numpy()
        self.tokenizer = tokenizer
        if args.gnn == "ReGGNN":
            self.gnn = ReGGNN(feature_dim_size=args.feature_dim_size,
                              hidden_size=args.hidden_size,
                              num_GNN_layers=args.num_GNN_layers,
                              dropout=config.hidden_dropout_prob,
                              residual=not args.remove_residual,
                              att_op=args.att_op)
        else:
            self.gnn = ReGCN(feature_dim_size=args.feature_dim_size,
                             hidden_size=args.hidden_size,
                             num_GNN_layers=args.num_GNN_layers,
                             dropout=config.hidden_dropout_prob,
                             residual=not args.remove_residual,
                             att_op=args.att_op)
        gnn_out_dim = self.gnn.out_dim
        self.classifier = PredictionClassification(config, args, input_size=gnn_out_dim)

    def forward(self, input_ids=None, labels=None):
        # construct graph
        if self.args.format == "uni":
            adj, x_feature = build_graph(input_ids.cpu().detach().numpy(), self.w_embeddings,
                                         window_size=self.args.window_size)
        else:
            adj, x_feature = build_graph_text(input_ids.cpu().detach().numpy(), self.w_embeddings,
                                              window_size=self.args.window_size)
        # initilizatioin
        adj, adj_mask = preprocess_adj(adj)
        adj_feature = preprocess_features(x_feature)
        adj = torch.from_numpy(adj)
        adj_mask = torch.from_numpy(adj_mask)
        adj_feature = torch.from_numpy(adj_feature)
        # run over GNNs
        outputs = self.gnn(adj_feature.to(device).double(), adj.to(device).double(), adj_mask.to(device).double())
        logits = self.classifier(outputs)
        prob = F.sigmoid(logits)
        if labels is not None:
            labels = labels.float()
            loss = torch.log(prob[:, 0] + 1e-10) * labels + torch.log((1 - prob)[:, 0] + 1e-10) * (1 - labels)
            loss = -loss.mean()

            return loss, prob
        else:
            return prob


# modified from https://github.com/saikat107/Devign/blob/master/modules/model.py
class DevignModel(nn.Module):
    def __init__(self, encoder, config, tokenizer, args):
        super(DevignModel, self).__init__()
        self.encoder = encoder
        self.config = config
        self.tokenizer = tokenizer
        self.args = args

        self.w_embeddings = self.encoder.roberta.embeddings.word_embeddings.weight.data.cpu().detach().clone().numpy()
        self.tokenizer = tokenizer

        self.gnn = GGGNN(feature_dim_size=args.feature_dim_size, hidden_size=args.hidden_size,
                         num_GNN_layers=args.num_GNN_layers, num_classes=args.num_classes,
                         dropout=config.hidden_dropout_prob)

        self.conv_l1 = torch.nn.Conv1d(args.hidden_size, args.hidden_size, 3).double()
        self.maxpool1 = torch.nn.MaxPool1d(3, stride=2).double()
        self.conv_l2 = torch.nn.Conv1d(args.hidden_size, args.hidden_size, 1).double()
        self.maxpool2 = torch.nn.MaxPool1d(2, stride=2).double()

        self.concat_dim = args.feature_dim_size + args.hidden_size
        self.conv_l1_for_concat = torch.nn.Conv1d(self.concat_dim, self.concat_dim, 3).double()
        self.maxpool1_for_concat = torch.nn.MaxPool1d(3, stride=2).double()
        self.conv_l2_for_concat = torch.nn.Conv1d(self.concat_dim, self.concat_dim, 1).double()
        self.maxpool2_for_concat = torch.nn.MaxPool1d(2, stride=2).double()

        self.mlp_z = nn.Linear(in_features=self.concat_dim, out_features=args.num_classes).double()
        self.mlp_y = nn.Linear(in_features=args.hidden_size, out_features=args.num_classes).double()
        self.sigmoid = nn.Sigmoid()

    def forward(self, input_ids=None, labels=None):
        # construct graph
        if self.args.format == "uni":
            adj, x_feature = build_graph(input_ids.cpu().detach().numpy(), self.w_embeddings)
        else:
            adj, x_feature = build_graph_text(input_ids.cpu().detach().numpy(), self.w_embeddings)
        # initilization
        adj, adj_mask = preprocess_adj(adj)
        adj_feature = preprocess_features(x_feature)
        adj = torch.from_numpy(adj)
        adj_mask = torch.from_numpy(adj_mask)
        adj_feature = torch.from_numpy(adj_feature).to(device).double()
        # run over GGGN
        outputs = self.gnn(adj_feature.to(device).double(), adj.to(device).double(),
                           adj_mask.to(device).double()).double()
        #
        c_i = torch.cat((outputs, adj_feature), dim=-1)
        batch_size, num_node, _ = c_i.size()
        Y_1 = self.maxpool1(nn.functional.relu(self.conv_l1(outputs.transpose(1, 2))))
        Y_2 = self.maxpool2(nn.functional.relu(self.conv_l2(Y_1))).transpose(1, 2)
        Z_1 = self.maxpool1_for_concat(nn.functional.relu(self.conv_l1_for_concat(c_i.transpose(1, 2))))
        Z_2 = self.maxpool2_for_concat(nn.functional.relu(self.conv_l2_for_concat(Z_1))).transpose(1, 2)
        before_avg = torch.mul(self.mlp_y(Y_2), self.mlp_z(Z_2))
        avg = before_avg.mean(dim=1)
        prob = self.sigmoid(avg)
        if labels is not None:
            labels = labels.float()
            loss = torch.log(prob[:, 0] + 1e-10) * labels + torch.log((1 - prob)[:, 0] + 1e-10) * (1 - labels)
            loss = -loss.mean()
            return loss, prob
        else:
            return prob


class GVDFG(nn.Module):
    def __init__(self, encoder, config, tokenizer, args):
        super(GVDFG, self).__init__()
        self.encoder = encoder
        self.config = config
        self.tokenizer = tokenizer
        self.args = args

        self.w_embeddings = self.encoder.roberta.embeddings.word_embeddings.weight.data.cpu().detach().clone().numpy()
        self.tokenizer = tokenizer
        if args.gnn == "ReGGNN":
            self.gnn1 = ReGGNN(feature_dim_size=args.feature_dim_size,
                               hidden_size=args.hidden_size,
                               num_GNN_layers=args.num_GNN_layers,
                               dropout=config.hidden_dropout_prob,
                               residual=not args.remove_residual,
                               att_op=args.att_op)
            self.gnn2 = ReGGNN(feature_dim_size=args.feature_dim_size,
                               hidden_size=args.hidden_size,
                               num_GNN_layers=args.num_GNN_layers,
                               dropout=config.hidden_dropout_prob,
                               residual=not args.remove_residual,
                               att_op=args.att_op)
        else:
            self.gnn1 = ReGCN(feature_dim_size=args.feature_dim_size,
                              hidden_size=args.hidden_size,
                              num_GNN_layers=args.num_GNN_layers,
                              dropout=config.hidden_dropout_prob,
                              residual=not args.remove_residual,
                              att_op=args.att_op)
            self.gnn2 = ReGCN(feature_dim_size=args.feature_dim_size,
                              hidden_size=args.hidden_size,
                              num_GNN_layers=args.num_GNN_layers,
                              dropout=config.hidden_dropout_prob,
                              residual=not args.remove_residual,
                              att_op=args.att_op)
        gnn_out_dim = self.gnn1.out_dim * 2
        self.classifier = PredictionClassification(config, args, input_size=gnn_out_dim)

    def forward(self, input_ids=None, labels=None):
        # construct graph
        adj, x_feature = build_graph(input_ids.cpu().detach().numpy(), self.w_embeddings,
                                     window_size=self.args.window_size)
        adjD, x_featureD = build_dfg(input_ids.cpu().detach().numpy(), self.w_embeddings, self.tokenizer)
        # initilizatioin
        adj, adj_mask = preprocess_adj(adj)
        adj_feature = preprocess_features(x_feature)
        adj = torch.from_numpy(adj)
        adj_mask = torch.from_numpy(adj_mask)
        adj_feature = torch.from_numpy(adj_feature)
        adjD, adj_maskD = preprocess_adj(adjD)
        adj_featureD = preprocess_features(x_featureD)
        adjD = torch.from_numpy(adjD)
        adj_maskD = torch.from_numpy(adj_maskD)
        adj_featureD = torch.from_numpy(adj_featureD)
        # run over GNNs
        outputs1 = self.gnn1(adj_feature.to(device).double(), adj.to(device).double(), adj_mask.to(device).double())
        outputs2 = self.gnn2(adj_featureD.to(device).double(), adjD.to(device).double(), adj_maskD.to(device).double())
        outputs = torch.cat((outputs1, outputs2), dim=1)
        logits = self.classifier(outputs)
        prob = F.sigmoid(logits)
        if labels is not None:
            labels = labels.float()
            loss = torch.log(prob[:, 0] + 1e-10) * labels + torch.log((1 - prob)[:, 0] + 1e-10) * (1 - labels)
            loss = -loss.mean()
            return loss, prob
        else:
            return prob


class Structer(nn.Module):
    def __init__(self, encoder, config, tokenizer, args):
        super(Structer, self).__init__()
        self.encoder = encoder
        self.config = config
        self.tokenizer = tokenizer
        self.args = args

        self.w_embeddings = self.encoder.roberta.embeddings.word_embeddings.weight.data.cpu().detach().clone().numpy()
        self.tokenizer = tokenizer

        if args.gnn == "ReGGNN":
            self.gnn1 = ReGGNN(feature_dim_size=args.feature_dim_size,
                               hidden_size=args.hidden_size,
                               num_GNN_layers=args.num_GNN_layers,
                               dropout=config.hidden_dropout_prob,
                               residual=not args.remove_residual,
                               att_op=args.att_op)
            self.gnn2 = ReGGNN(feature_dim_size=args.feature_dim_size,
                               hidden_size=args.hidden_size,
                               num_GNN_layers=args.num_GNN_layers,
                               dropout=config.hidden_dropout_prob,
                               residual=not args.remove_residual,
                               att_op=args.att_op)
        else:
            self.gnn1 = ReGCN(feature_dim_size=args.feature_dim_size,
                              hidden_size=args.hidden_size,
                              num_GNN_layers=args.num_GNN_layers,
                              dropout=config.hidden_dropout_prob,
                              residual=not args.remove_residual,
                              att_op=args.att_op)
            self.gnn2 = ReGCN(feature_dim_size=args.feature_dim_size,
                              hidden_size=args.hidden_size,
                              num_GNN_layers=args.num_GNN_layers,
                              dropout=config.hidden_dropout_prob,
                              residual=not args.remove_residual,
                              att_op=args.att_op)
        gnn_out_dim = self.gnn1.out_dim
        self.classifier = PredictionClassification(config, args, input_size=gnn_out_dim)

    def forward(self, input_ids=None, labels=None):
        # extract code
        # code = self.tokenizer.decode(input_ids.cpu().detach().numpy(), skip_special_tokens=True)
        # construct graph
        adj, x_feature = build_dfg(input_ids.cpu().detach().numpy(), self.w_embeddings, self.tokenizer)
        # adjD, x_featureD = build_dfg(input_ids.cpu().detach().numpy(), self.w_embeddings, self.tokenizer)
        # initilizatioin
        adj, adj_mask = preprocess_adj(adj)
        adj_feature = preprocess_features(x_feature)
        adj = torch.from_numpy(adj)
        adj_mask = torch.from_numpy(adj_mask)
        adj_feature = torch.from_numpy(adj_feature)
        # adjD, adj_maskD = preprocess_adj(adjD)
        # adj_featureD = preprocess_features(x_featureD)
        # adjD = torch.from_numpy(adjD)
        # adj_maskD = torch.from_numpy(adj_maskD)
        # adj_featureD = torch.from_numpy(adj_featureD)
        # run over GNNs
        outputs1 = self.gnn1(adj_feature.to(device).double(), adj.to(device).double(), adj_mask.to(device).double())
        # outputs2 = self.gnn2(adj_featureD.to(device).double(), adjD.to(device).double(), adj_maskD.to(device).double())
        # outputs = torch.cat((outputs1, outputs2), dim=1)
        logits = self.classifier(outputs1)
        prob = F.sigmoid(logits)
        if labels is not None:
            labels = labels.float()
            loss = torch.log(prob[:, 0] + 1e-10) * labels + torch.log((1 - prob)[:, 0] + 1e-10) * (1 - labels)
            loss = -loss.mean()
            return loss, prob
        else:
            return prob


class GraphCodeBERT(nn.Module):
    def __init__(self, encoder, config, tokenizer, args):
        super(GraphCodeBERT, self).__init__()
        self.encoder = encoder
        self.config = config
        self.tokenizer = tokenizer
        self.args = args
        self.query = 0

    def forward(self, inputs_ids=None, attn_mask=None, position_idx=None, labels=None):
        nodes_mask = position_idx.eq(0)
        token_mask = position_idx.ge(2)

        inputs_embeddings = self.encoder.roberta.embeddings.word_embeddings(
            inputs_ids)
        nodes_to_token_mask = nodes_mask[:, :, None] & token_mask[:, None, :] & attn_mask
        nodes_to_token_mask = nodes_to_token_mask / \
                              (nodes_to_token_mask.sum(-1) + 1e-10)[:, :, None]
        avg_embeddings = torch.einsum(
            "abc,acd->abd", nodes_to_token_mask, inputs_embeddings)
        inputs_embeddings = inputs_embeddings * \
                            (~nodes_mask)[:, :, None] + avg_embeddings * nodes_mask[:, :, None]
        outputs = self.encoder(inputs_embeds=inputs_embeddings,
                               attention_mask=attn_mask, position_ids=position_idx)[0]

        logits = outputs
        prob = F.sigmoid(logits)
        if labels is not None:
            labels = labels.float()
            loss = torch.log(prob[:, 0] + 1e-10) * labels + \
                   torch.log((1 - prob)[:, 0] + 1e-10) * (1 - labels)
            loss = -loss.mean()
            return loss, logits
        else:
            return prob
