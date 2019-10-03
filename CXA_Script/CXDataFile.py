#coding=utf-8

import os, sys
import CXA_Rely.get_project_path as Cp

class GetAsseatData(object):
    def __init__(self):
        self.custom_library_path = ''
        self.moudle_dict = {}
        self.create_moudle_data()

    def get_moudle_data(self,path):
        return os.listdir(path)

    def create_moudle_data(self):

        for moudle in self.get_moudle_data(Cp.get_library_path()):
            type_moudel = {}
            self.moudle_dict[moudle] = type_moudel
            moudel_path = '{moudel_name}'.format(moudel_name=moudle)
            library_path = Cp.get_library_path()
            self.moudle_list = os.path.join(library_path, moudel_path)

            for type in os.listdir(self.moudle_list):
                item_moudle = {}
                moudel_path = '{moudel_name}/{tree}'.format(moudel_name=moudle, tree=type)
                library_path = Cp.get_library_path()
                self.type_list = os.path.join(library_path, moudel_path)
                type_moudel[type] = item_moudle

                for child in os.listdir(self.type_list):
                    moudel_path = '{moudel_name}/{tree}/{child}'.format(moudel_name=moudle, tree=type,child=child)
                    library_path = Cp.get_library_path()
                    self.child_list = os.path.join(library_path, moudel_path)
                    child_moudle = self.create_list_item_data(self.child_list,type)
                    item_moudle[child] = child_moudle


    def create_list_item_data(self,list_item_path,type):
        item_dict = {}

        self.asseat_path = list_item_path

        for child in os.listdir(self.asseat_path):
            file_path = self.asseat_path + '/{a}'.format(a=child)
            if not os.path.isfile(file_path):
                print file_path
                samp_info_data = {}
                item_dict[child] = samp_info_data
                samp_icon = self.asseat_path+'/{i}/{i}.jpg'.format(i=child)
                samp_name = child
                samp_type = type
                samp_file_type = 'file_type' #todo: 这里要换成函数解析当前文件类型
                samp_file_size = '10M'
                samp_data = '20181209'
                samp_version = [] #todo：需要函数列出选择文件下的同类型文件数量
                samp_import = self.asseat_path+'/{i}/{i}.{type}'.format(i=child,type=samp_file_type)

                samp_info_data['samp_icon'] = samp_icon
                samp_info_data['samp_name'] = samp_name
                samp_info_data['samp_type'] = samp_type
                samp_info_data['samp_file_type'] = samp_file_type
                samp_info_data['samp_file_size'] = samp_file_size
                samp_info_data['samp_data'] = samp_data
                samp_info_data['samp_version'] = samp_version
                samp_info_data['samp_import'] = samp_import

        return item_dict

    def get_file_type(self,file_path):
        print 'get_file_type%s' %file_path


if __name__ == '__main__':
    Gad = GetAsseatData()
    Gad.create_moudle_data()
    print Gad.moudle_dict