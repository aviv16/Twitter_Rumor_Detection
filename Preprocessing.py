import xlrd
import re
from xlwt import Workbook
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from os import path

N = 50
Min = 5
K = 500


class PreprocessingHelper:

    # Cleans empty cells/lines, removing non-alphabet characters and change to lowercase
    def prepareData(self, input_file, output_file):
        output_row = 0
        output_col = 0
        exist_in_row_flag = False
        regex = "[^a-zA-Z0-9 ]"
        http_regex = '(?:\s)http[^ ]*'

        write_wb = Workbook()
        write_sheet = write_wb.add_sheet('Sheet 1')

        read_wb = xlrd.open_workbook(input_file)
        read_sheet = read_wb.sheet_by_index(0)

        for row in range(read_sheet.nrows):
            for col in range(read_sheet.ncols):
                cell_text = read_sheet.cell_value(row, col)
                if col == 0:
                    eid = cell_text
                elif col == 1:
                    classification = cell_text
                elif cell_text != '':
                    prepared_text = re.sub(http_regex, "", cell_text)
                    prepared_text = re.sub(regex, "", prepared_text)
                    prepared_text = prepared_text.lower()  # all in lower case
                    if prepared_text.islower():
                        if not exist_in_row_flag:
                            write_sheet.write(output_row, 0, eid)
                            write_sheet.write(output_row, 1, classification)
                            output_col = 2
                    #if prepared_text != '' or prepared_text != ' ':
                        write_sheet.write(output_row, output_col, prepared_text)
                        output_col = output_col + 1
                        exist_in_row_flag = True

            if exist_in_row_flag:
                output_row = output_row + 1
            output_col = 0
            exist_in_row_flag = False
        write_wb.save(output_file)


    # Reading file and split into events.
    # The file must be cleaned (prepareData func) before use in this function.
    def splitFileToEvents(self, file_name):
        event_list = []
        event_posts = []
        event_ids = []
        file = xlrd.open_workbook(file_name)
        sheet = file.sheet_by_index(0)
        prev_eid = sheet.cell_value(0, 0)
        prev_class = sheet.cell_value(0, 1)
        event_classification = []
        for row in range(sheet.nrows):
            empty_line_flag = False
            col = 0
            while col < sheet.ncols and not empty_line_flag:
                if col == 0 and row != 0:
                    if sheet.cell_value(row, col) != prev_eid:
                        event_classification.append(prev_class)
                        prev_class = sheet.cell_value(row, col+1)
                        event_ids.append(prev_eid)
                        prev_eid = sheet.cell_value(row, col)
                        event_list.append(event_posts.copy())
                        event_posts.clear()
                        col = 2
                    else:
                        col = 2
                if sheet.cell_value(row, col) != '':
                    if col > 1:
                        event_posts.append(sheet.cell_value(row, col))
                else:
                    empty_line_flag = True
                col = col + 1
        event_list.append(event_posts.copy()) # Add last event
        event_classification.append(prev_class)
        event_ids.append(prev_eid)
        return event_list, event_classification, event_ids


    # Creating post series according to Alg.1
    def createPostSeries(self, event):
        v = 1
        x = 0
        y = 0
        post_series = np.array([])
        if len(event) >= N * Min:
            size_of_series = N
            while v <= len(event) // N:
                x = size_of_series * (v - 1)
                y = size_of_series * v
                if x == 0:
                    post_series = np.array([event[x:y]])
                else:
                    post_series = np.append(post_series, [event[x:y]], axis=0)
                v = v + 1
        else: #event.__len__() < N * Min
            print("event too small. Should be padded earlier..")
            size_of_series = len(event)//Min
            while (v < Min):
                x = size_of_series * (v - 1)
                y = size_of_series * v
                if x == 0:
                    post_series = np.array([event[x:y]])
                else:
                    post_series = np.append(post_series, [event[x:y]], axis=0)
                v = v + 1
        #Add leftovers
        if len(event) != y:
            x = size_of_series * (v - 1)
            y = size_of_series * v
            if len(event) != size_of_series * v:
                if len(event) < size_of_series * v:
                    event[len(event):size_of_series * v] = (size_of_series * v - len(event))*[0]
                else:
                    event = event[:size_of_series * v]
            post_series = np.append(post_series, [event[x:y]], axis=0)
        return post_series

    # calculating the TF-IDF of all posts
    def calculateTFIDF(self, event):
        vectorizer = TfidfVectorizer(max_features=K)
        vectors = vectorizer.fit_transform(event)
        # feature_names = vectorizer.get_feature_names()
        dense = vectors.todense()
        return dense.tolist()

    # pad an event so that its length will be: N*Min + N*i (where i can be 0,1,2...)
    # Eventually, the event will be separated to post series easily
    def padEvent(self, event):
        leftover = 0
        event_len = len(event)
        if event_len < N * Min:
            leftover = N * Min - event_len
            event[event_len:N * Min] = leftover * [""]

        elif event_len % N != 0:
            modulo = event_len % N
            leftover = N - modulo
            event[event_len:event_len + leftover] = leftover * [""]
        return event, leftover

    # get all the post from all events
    def getAllEvents(self, data):
        all_posts = []
        padded_posts_to_event_count = []
        for event in data:
            posts, added_posts_cnt = self.padEvent(event)
            all_posts += posts
            padded_posts_to_event_count.append(added_posts_cnt)
        return all_posts, padded_posts_to_event_count

    # get the data from the dataset's file.
    # In this function the data will eventually be split to x = post series, y = classification
    def getData(self, dataset_file, progressBar):
        # file of cleaned data
        to_replace = ".xls"
        if dataset_file.endswith(".xlsx"):
            to_replace = ".xlsx"
        res_file_name = dataset_file.replace(to_replace,"_RES.xls")
        if path.exists(res_file_name):
            print("############# "+res_file_name+" already exist! Not Overwriting! #############")
        else: # cleaning the data from unwanted characters
            self.prepareData(dataset_file,res_file_name)

        data, classification, event_ids = self.splitFileToEvents(res_file_name)
        _x_train = np.array([])
        _y_train = np.array([])
        _y_train1 = np.array([])
        all_posts, padded_posts_to_event_count = self.getAllEvents(data)
        total_tf_idf = self.calculateTFIDF(all_posts)
        i = 0
        prev_posts_num = 0
        # the entire data TF-IDF is calculated. now splitting to post series
        for event in data:
            progressBar.setValue(((i+1)/len(data))*100)
            print('~~~~~~~~~~ Event id = '+event_ids[i]+' ~~~~~~~~~~')
            print('~~~~~~~~~~ Num of posts = ' + str(event.__len__()) + ' ~~~~~~~~~~')
            event_tf_idf = total_tf_idf[prev_posts_num:prev_posts_num + len(event)]
            prev_posts_num = prev_posts_num + len(event)
            post_series = self.createPostSeries(event_tf_idf)
            if i == 0:
                _x_train = np.array(post_series)
            else:
                _x_train = np.append(_x_train,post_series, axis=0)
            # save the corresponding classification of each post series
            _y_train = np.append(_y_train, len(post_series)*[int(classification[i])], axis=0)
            i += 1
        return _x_train, _y_train


if __name__ == "__main__":
    i=0
    #prepareData('test_test.xls', 'test_res_4.xls')
    # data, classification = splitFileToEvents('test_res_4.xls')
    # #data = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10','11', '12', '13', '14', '15', '16', '17', '18', '19']
    # #data = dataPreparation('test_test.xls')
    # K = 100  # Only for testing
    # x_train = np.array([])
    # y_train = np.array([])
    # i = 0
    # for event in data:
    #     print('~~~~~~~~~~ Event id = '+event[0]+' ~~~~~~~~~~')
    #     print('~~~~~~~~~~ Num of posts = ' + str(event.__len__() - 2) + ' ~~~~~~~~~~')
    #     tf_idf = calculateTFIDF(event[2:])
    #     num_of_words = min(K, tf_idf.__len__())
    #     post_series = createPostSeries(tf_idf)
    #     X_train = np.append(x_train, sequence.pad_sequences(post_series, maxlen=K, dtype='double', truncating='post'))
    #     for batch in range(len(post_series)):
    #         y_train = np.append(y_train, classification[i])
    #     i += 1
    #     print(post_series)

