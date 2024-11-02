import re
import numpy as np
file_path = 'configure.txt'  # configure文件路径
source_path='src'      # 默认资源文件夹路径
module_out='out'

def extract_lines_between_markers(file):
    lines_array = []
    record = False  # 标记是否在开始记录
    begin_count = 0  # 记录 'module:begin' 的数量

    for line in file:
        # 检查是否遇到开始标记
        if 'module:begin' in line:
            record = True
            begin_count += 1
            continue  # 跳过这一行

        # 检查是否遇到结束标记
        if 'end' in line:
            if begin_count == 0:
                raise ValueError(f"Error: 'end' found without matching 'module:begin' in {file_path}")
            record = False
            begin_count -= 1
            break  # 退出循环

        # 如果在记录状态，则将行添加到数组
        if record:
            lines_array.append(line.strip())  # 去掉行末尾的换行符

    # 如果有未匹配的 'module:begin'
    if begin_count > 0:
        raise ValueError(f"Error: Unmatched 'module:begin' found in {file_path}")

    return lines_array

def find_port(module):
    port=[]
    port_width=[]
    filename=source_path+'/'+module+'.v'
    flag=False
    with open(filename,encoding='utf-8') as file:
        for line in file:
            line=line.split('//')[0]
            line=line.split('/*')[0]
            if line.strip()=='':
                continue
            if 'module' in line:
                flag=True
                continue
            if flag:
                if ('input' in line or 'output' in line):
                    matches = re.findall(r'\[(.*?)\]', line)
                    if matches:
                        port_width.append(matches[0]) # 有中括号则添加匹配的内容
                    else:
                        port_width.append('1')  # 没有中括号则添加 '1'
                    temp=line.split()[-1]
                    temp=temp.split(']')[-1]
                    temp=temp.strip(',')
                    port.append(temp)
            if ');' in line:
                break

        if port is None:
            raise ValueError(f"Error: 'port' not found in {filename}")
        return port,port_width


def extract_connect_parameters(file):
    parameters = None
    flag=False
    for line in file:
        # 使用正则表达式匹配 connect 函数
        match = re.search(r'connect\(([^,]+),\s*([^}]+)\):begin', line)
        if match:
            # 提取 module_a和  module_b
            module_a = match.group(1).strip()
            module_b = match.group(2).strip()
            index_a = lines.index(module_a)
            index_b = lines.index(module_b)
            parameters = (index_a, index_b)
            flag=True
            continue
        if 'end' in line:
            flag=False
            continue
        if flag:
            t=line.strip().split('-')
            matrixdex_a = cum_num[index_a] + int(t[0]) - 1
            matrixdex_b = cum_num[index_b] + int(t[-1]) - 1
            matrix[matrixdex_a][matrixdex_b]=1
    if flag:
        raise ValueError(f"Error: Unmatched 'end'.Please check")
    if parameters is None:
        raise ValueError(f"Error: No matching 'connect(module_a, module_b):begin' found in {file_path}")

    return


keyname=[]
datawidth=[]
num_array=[]
try:
    with open(file_path, 'r') as file:
        first_line = file.readline()
        if 'source_path' not in first_line:
            raise ValueError(f"Error: '{source_path}' not found in {file_path}")
        else:
            source_path=first_line.split(':')[-1].strip()
        second_line = file.readline()
        if 'module_out' not in second_line:
            raise ValueError(f"Error: '{module_out}' not found in {file_path}")
        else:
            module_out=second_line.split(':')[-1].strip()
        lines = extract_lines_between_markers(file)
        for line in lines:
            port,port_width = find_port(line)
            num_array.append(len(port))
            datawidth=datawidth+port_width
            for p in port:
                keyname.append(line+'_'+p)
        size = len(keyname)
        cum_num_o = np.cumsum(num_array)
        if len(cum_num_o) > 0:
            cum_num = np.insert(cum_num_o, 0, 0)  # 添加0并去掉最后一个元素
            cum_num = cum_num[:-1]
        else:
            cum_num = [0]  # 如果数组为空，返回只有0的数组
        matrix = [[0 for _ in range(size)] for _ in range(size)]
        extract_connect_parameters(file)
except ValueError as e:
    print(e)




portname=[None]*size
port=[]
for _ in range(len(keyname)):
    port.append(keyname[_].split('-')[-1])
for i in range(size):
    for j in range(size):
        if(matrix[i][j]):
            portname[i]=keyname[i]
            portname[j]=keyname[i]
            if datawidth[i]!=datawidth[j]:
                t1=keyname[i].replace('_','-')
                t2 = keyname[j].replace('_', '-')
                print(f'Warning: datawidth of {t1} and {t2} does not match')

file_out=module_out+'.v'
with open(file_out, 'w') as file:
    file.write('module '+module_out+'(\n')
    file.write('\n')
    file.write(');\n')
    file.write('\n')

    for i in range(size):
        if np.sum(matrix[i]) > 0:
            if datawidth[i]!='1':
                file.write('wire ['+datawidth[i]+'] '+portname[i]+';\n')
            else:
                file.write('wire'+' '+portname[i]+';\n')
    file.write('\n')
    file.write('\n')
    for i in range(len(lines)):
        file.write(lines[i] + ' ' +lines[i] + '0' + '(\n')
        offset=cum_num[i]
        for j in range(num_array[i]):
            if portname[offset+j]!=None:
                temp=portname[offset+j]
            else:
                temp=''
            st=port[offset+j]
            st=st[st.find('_')+1:]
            if j!=num_array[i]-1:
                file.write('.'+st+'('+temp+'),\n')
            else:
                file.write('.'+st+'('+temp+')\n')
        file.write(');\n')
        file.write('\n')