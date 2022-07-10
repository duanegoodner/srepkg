import command_input as ci
import repackager as rep
import service_class_builder as scb


def main(args):
    srepkg_command = ci.SrepkgCommandLine().get_args()
    service_class_builder = scb.ServiceClassBuilder()
    repackager = rep.Repackager(srepkg_command, service_class_builder)

    # srepkg_command = command_line.get_args(*args)
    # service_class_builder = ServiceClassBuilder()
    # construction_dir = service_class_builder\
    #     .build_construction_dir(srepkg_command.construction_dir)
    # construction_dir.rename_sub_dirs('parent', 'child')
    # print(construction_dir)


if __name__ == '__main__':
    main(['hello'])


