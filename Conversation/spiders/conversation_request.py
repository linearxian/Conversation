# -*- coding: utf-8 -*-
import re
import requests
import time


def parse_Answer(q_id):
    i = 1
    out = open("./Output/Answer.txt", "a")
    while True:
        with requests.session() as MySession:
            url = 'http://question.jd.com/question/getAnswerListById.action'
            data = {
                'questionId':'%s' %q_id,
                'page':i
            }
            data = MySession.get(url, params = data).text
            if data:
                lines = re.findall('"content":"(.*?)"', data)
                if lines:
                    for line in lines:
                        print(line)
                        out.write(line)
                        out.write("\n")
                else:
                    print('--------------Parse Question Finished--------------')
                    out.close()
                    break
            else:
                print('--------------Parse Question Error--------------')
                out.close()
                break
            i = i + 1
            time.sleep(5)

def parse_Product(p_id):
    i = 1
    out = open("./Output/Question.txt", "a")
    while True:
        with requests.session() as MySession:
            url = 'http://question.jd.com/question/getQuestionAnswerList.action'
            API = {
                'productId':'%s' %p_id,
                'page':i
            }
            data = MySession.get(url, params = API).text
            if data:
                lines = re.findall(r'"id":(\d+),"content":"(.*?)"', data)
                loop = 1
                if lines:
                    for QID,Question in lines:
                        print(Question)
                        out.write(Question)
                        out.write("\n")
                        parse_Answer(QID)
                        loop = loop + 1
                else:
                    print('--------------Parsing Product Finished--------------')
                    out.close()
                    break

            else:
                print('--------------Parsing Product Error--------------')
                out.close()
                break
            i = i + 1
            time.sleep(5)

def run():
    with open("./PID/PID_babycare.json") as f:
        for line in f:
            try:
                pid = re.findall(r'"PID": "(.*?)"', line)[0]
                parse_Product(pid)
            except IndexError:
                pass

if __name__ == '__main__':
    run()