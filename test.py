import imaplib
import json
import os
import poplib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

cron_map = {
    1: '5 0-2',
    2: '15 0-2',
    3: '25 0-2',
    4: '35 0-2',
    5: '45 0-2',
    6: '5 3-5',
    7: '15 3-5',
    8: '25 3-5',
    9: '35 3-5',
    10: '45 3-5',

    11: '5 6-8',
    12: '15 6-8',
    13: '25 6-8',
    14: '35 6-8',
    15: '45 6-8',
    16: '5 9-11',
    17: '15 9-11',
    18: '25 9-11',
    19: '35 9-11',
    20: '45 9-11',
}


def get_bj_time():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    return int(utc_dt.astimezone(timezone(timedelta(hours=8))).strftime('%H'))


u_name = 'maming'


def gen_yml():
    p = Path(f'.azure/hua1.yml')
    for j in range(1, 100):
        new_file = Path(f'.azure/{u_name}{j}.yml')
        string = p.read_text()
        string = string.replace('$USERNAME1', f'$USERNAME{j}').replace('PARENT_USER: atzouhua', 'PARENT_USER: atmaming')
        new_file.write_text(string)


# gen_yml()
# exit()


def execute(_cmd):
    return json.loads(os.popen(_cmd).read())


def run():
    data = os.popen('az pipelines list')
    data = json.loads(data.read())
    for i in data:
        os.system(f"az pipelines delete --id {i['id']} --yes")


username = '0001@menwloc.onmicrosoft.com|atcaoyufei1'
data = username.split('|')
organization = data[1]
project = data[1]
user = []
cmd_list = []

login_cmd = f'az login --allow-no-subscriptions -u {data[0]} -p hack3321!'
os.system(login_cmd)

os.system(f'az devops configure --defaults organization=https://dev.azure.com/{organization} project={project}')
group_data = execute('az pipelines variable-group list')
if not len(group_data):
    execute('az pipelines variable-group create --name huawei --authorize true --variables PASSWORD=hack3321')
    group_data = execute('az pipelines variable-group list')
group_id = group_data[0]['id']

data = execute('az devops service-endpoint list')
if not len(data):
    os.environ.setdefault('AZURE_DEVOPS_EXT_GITHUB_PAT', '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')
    execute('az devops service-endpoint github create --github-url https://github.com/a224327780 --name a224327780')
    data = execute('az devops service-endpoint list')
service_id = data[0]['id']

variable_cmd = f'az pipelines variable-group variable create --group-id {group_id}'

pip = 'az pipelines create --name {} --description {} --repository https://github.com/a224327780/hw --branch master --yml-path .azure/{}{}.yml --service-connection {}'

pip_cmd_list = []
variable_cmd_list = []
j = 1
for i in range(1, 101):
    n = f'0{i}' if int(i) >= 10 else f'00{i}'
    if i >= 100:
        n = i

    if len(user) < 5:
        name = f'{u_name}{n}'
        user.append(name)

    if len(user) == 5 or i == 199:
        pip_name = f'{user[0]}-{user[-1]}'.replace(u_name, '')
        USERNAME = ','.join(user)
        variable_cmd_list.append(f"{variable_cmd} --name USERNAME{j} --value {USERNAME}")
        pip_cmd_list.append(pip.format(pip_name, pip_name, u_name, j, service_id))
        j += 1
        user = []

for cmd in variable_cmd_list:
    # os.system(cmd)
    print(cmd)

for cmd in pip_cmd_list:
    # os.system(cmd)
    print(cmd)
