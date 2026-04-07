import sys
import traceback

old_e = "return jsonify({\"error\": f\"发生错误: {str(e)}\"}), 500"
new_e = "traceback.print_exc()\n        return jsonify({\"error\": f\"发生错误: {str(e)}\"}), 500"

with open(r'd:\AGenticVul\3s_back\app.py', 'r', encoding='utf-8') as f:
    c = f.read()

if "import traceback" not in c:
    c = "import traceback\n" + c

c = c.replace(old_e, new_e)

with open(r'd:\AGenticVul\3s_back\app.py', 'w', encoding='utf-8') as f:
    f.write(c)

