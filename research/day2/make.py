import glob
import os
import subprocess


def make():
    os.chdir('code/')
    sql_list = []
    for item in sorted(os.listdir()):
        if item.endswith(".sql"):
            sql_list.append(item)

    for i in range(10):
        prefix = f'step{i}'
        for item in sql_list:
            if prefix in item:
                print(item)
                command = f'docker exec -it db psql -U postgres -d empire-erp -f {item}'
                subprocess.run(command.split(' '))

        for filename_with_query in glob.glob("*.cmd"):
            if prefix in filename_with_query:
                filename_without_ext = os.path.splitext(filename_with_query)[0]
                print(filename_without_ext)

                with open(filename_with_query, "r") as cmdfile:
                    with open(f'{filename_without_ext}.mk', "w") as fmake:
                        fmake.write(f'\\i {filename_with_query}\n')
                        fmake.write(f'\\o {filename_without_ext}.out\n')
                        fmake.write(cmdfile.read())

                command = f'docker exec -it db psql -U postgres -d empire-erp -f {filename_without_ext}.mk'
                subprocess.run(command.split(' '))

    os.chdir('../')
    command = f'markdown-pp README.mdpp -o README.md'
    subprocess.run(command.split(' '))

    os.chdir('code/')
    for item in os.listdir():
        if item.endswith(".mk") or item.endswith(".out") :
            os.remove(item)


if __name__ == "__main__":
    make()
