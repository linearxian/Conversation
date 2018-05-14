# -*- coding: utf-8 -*-
import re
import requests
import time


def parse_Product(p_id):
    i = 0
    review_old = []
    title_old = []
    out_title = open("./Output/Title.txt", "a")
    out_review = open("./Output/Review.txt", "a")
    while i < 10:
        with requests.session() as MySession:
            url = 'http://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv50941&productId={0}&score=0&sortType=5&page={1}&pageSize=10&isShadowSku=0&rid=0&fold=1'.format(p_id, i)
            try:
                data = MySession.get(url).text
                if data:
                    titles = re.findall(r'"referenceName":"(.*?)"', data)
                    reviews = re.findall(r'"content":"(.*?)"', data)
                    if titles:
                        title = titles[0]
                        if title != title_old:
                            print(title)
                            out_title.write(title)
                            out_title.write("\n")
                            title_old = title
                    if reviews:
                        print('--------------Parsing Page %s--------------' % i)
                        for review in reviews:
                            if review != review_old:
                                # print(review)
                                out_review.write(review)
                                out_review.write("\n")
                                review_old = review
                    else:
                        print('--------------Parsing Product Finished--------------')
                        out_title.close()
                        out_review.close()
                        break

                else:
                    print('--------------Response Error--------------')
                    out_title.close()
                    out_review.close()
                    break
                i = i + 1
                time.sleep(5)
            except:
                print('--------------Parsing Product Error--------------')
                out_title.close()
                out_review.close()
                break

def run():
    with open("./PID/PID_c1_1.json") as f:
        for line in f:
            try:
                pid = re.findall(r'"PID": "(.*?)"', line)[0]
                parse_Product(pid)
            except:
                pass

if __name__ == '__main__':
    run()