import os
import subprocess


def make():
    os.chdir('code/')
    for item in sorted(os.listdir()):
        if item.endswith(".sql"):
            print(item)
            command = f'docker exec -it db psql -U postgres -d empire-erp -f {item}'
            subprocess.run(command.split(' '))
        elif item.endswith(".sqlx"):
            cmd_file = item
            print(cmd_file)
            filename_without_ext = os.path.splitext(cmd_file)[0]
            with open(cmd_file, "r") as cmdfile:
                with open(f'{filename_without_ext}.mk', "w") as fmake:
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
