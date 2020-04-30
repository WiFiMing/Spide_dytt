import os

class TXTwriter:
    def get_filepath(self):
        """获取结果文件路径"""
        file_path = os.path.split(
            os.path.realpath(__file__))[0] + os.sep + '输出txt文本' + os.sep

        if not os.path.isdir(file_path):
            os.makedirs(file_path)

        return file_path

    def write_out(self, book_name, movie_info):
        """将章节内容写入txt文本"""
        writein = u'电影名称：' + movie_info['title'] + \
        u'\n上映时间：' + movie_info['release_date'] + \
        u'\n豆瓣评分：' + movie_info['score'] + '\n\n'
        with open(self.get_filepath()+book_name, 'a+', encoding='gb2312') as f:
            f.write(writein)