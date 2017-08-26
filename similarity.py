# encoding:utf-8


def generateSourcefile(glossaryfile, xiepeiyidic):
    result_ = []
    with open(glossaryfile, 'rt') as greader, open(xiepeiyidic, 'rt') as xreader:
        glines = greader.readlines()
        xlines = xreader.readlines()
        for gl in glines:
            gl = gl.split()
            pos = gl[1]
            gl = gl[0]
            if pos == 'V':
                for xl in xlines:
                    result_.append(gl + '\t' + xl)
    return result_


def empty(line):
    if isinstance(line, str):
        line = line.strip()
        if line == '':
            return True
        else:
            return False
    elif isinstance(line, list):
        if line == []:
            return True
        else:
            return False
    elif isinstance(line, dict):
        if line == {}:
            return True
        else:
            return False
    else:
        print('function empty() has error!!\ninput type is ' + type(line) + '\n')


def parseZhAndEn(text):  # 分割描述式中的中文和英文义原
    words = text.split('|')
    if len(words) == 2:
        return words[1], words[0]
    else:
        return text, text


# 词汇表条目
class GlossaryElement:
    def __init__(self):
        self.word = ''  # 词
        self.type = ''  # 词性
        self.solid = False  # 实词/虚词
        self.s_first = ''  # 第一基本义原
        self.s_other = []  # 其他义原
        self.s_relation = {}  # 关系义原
        self.s_symbol = {}  # 符号义原

    def dump(self):
        print(self.word + ',' + self.type + ', | first:' + self.s_first + ' | other:')
        for i in range(len(self.s_other)):
            print(self.s_other[i] + ',')

        print(' | relation:')
        for it in self.s_relation.keys():
            print(it + '=' + self.s_relation[it] + ',')

        print(' | symbol:')
        for it in self.s_symbol.keys():
            print(it + '=' + self.s_symbol[it] + ',')

        print('\n')

    def parse(self, text):

        line = text

        if empty(line):
            return False
        items = line.split()
        if len(items) == 3:
            self.word = items[0]
            self.type = items[1]
            if line[0] != '{':  # 判断实词、虚词
                self.solid = True
            else:
                self.solid = False
                line = line[1:len(line) - 2]

            sememes = items[2].split(',')

            if len(sememes) > 0:
                firstdone = False
                if sememes[0][0].isalpha():
                    self.s_first, defaultText = parseZhAndEn(sememes[0])
                    firstdone = True

                for i in range(len(sememes)):
                    if i == 0 and firstdone:
                        continue

                    firstletter = sememes[i][0]
                    if '(' == firstletter:
                        self.s_other.append(sememes[i])
                        continue
                    equalpos = sememes[i].find('=')
                    if equalpos != -1:
                        key = sememes[i][0:equalpos]
                        value = sememes[i][equalpos + 1]
                        if len(value) > 0 and value[0] != '(':
                            value, defaultText = parseZhAndEn(value)
                        self.s_relation[key] = value
                        continue

                    if firstletter.isalpha() is False:
                        value = sememes[i][1:]
                        if len(value) > 0 and value[0] != '(':
                            value, defaultText = parseZhAndEn(value)
                        self.s_symbol[firstletter] = value
                        continue
                    self.s_other.append(sememes[i])
            # self.dump()
            return True
        return False


# 义原条目
class SememeElement:
    def __init__(self):
        self.id = -1  # 编号
        self.father = -1  # 父义原编号
        self.sememe_zh = ''  # 中文义原
        self.sememe_en = ''  # 英文义原

    def parse(self, line):  # line指的是WHOLEDAT中1618个义原的数据形式
        if empty(line) is True:
            return False
        items = line.split()
        if len(items) == 3:
            self.id = items[0]
            self.father = items[2]
            self.sememe_zh, self.sememe_en = parseZhAndEn(items[1])
            return True
        return False


def isInGlossarytable_(keys, word):
    for key_ in keys:
        key_ = key_.split()[1]
        if word == key_:
            return True
    return False


def valuesOfGlossarytable_(glossarytable_, word):
    values_ = []
    for key_, v_ in glossarytable_.items():
        key_ = key_.split()[1]
        if key_ == word:
            values_.append(v_)
    return values_


class WordSimilarity:
    def __init__(self):
        self.sememetable_ = dict()  # 义原表
        self.sememeindex_zn_ = dict()  # 义原索引(中文)
        self.glossarytable_ = dict()  # 词汇表

    # 初始化义原和词汇表
    def init(self, sememefile, glossaryfile):

        if self.loadSememeTable(sememefile) is False:
            print("[ERROR] %s load failed.", sememefile)
            return False
        if self.loadGlossary(glossaryfile) is False:
            print("[ERROR] %s load failed.", glossaryfile)
            return False
        return True

    def loadSememeTable(self, filename):
        with open(filename, 'rt') as reader:
            try:
                lines = reader.readlines()
                for line in lines:
                    if empty(line) is False:
                        ele = SememeElement()  # 对象whole
                        if ele.parse(line):
                            self.sememetable_[ele.id] = ele  # dict
                            self.sememeindex_zn_[ele.sememe_zh] = ele  # 中文dict
            except Exception as e:
                print('function loadSememeTable has Errors!!')
                print(e)
                return False
        return True

    # 加载词汇表
    def loadGlossary(self, filename):

        with open(filename, 'rt') as reader:
            try:
                lines = reader.readlines()
                if lines is []:
                    return False
                count = 0
                for line in lines:
                    if empty(line) is False:
                        ele = GlossaryElement()  # 对象glossary
                        if ele.parse(line):
                            self.glossarytable_[str(count) + '\t' + ele.word] = ele
                            count = count + 1
                print('function loadGlossary has been completed!!')
            except Exception as e:
                print('function loadGlossary has errors!!')
                print(e)
                return False
        return True

    # 根据编号获取义原
    def getSememeByID(self, id_):

        if id_ in self.sememetable_.keys():
            return self.sememetable_[id_]
        return None

    # 根据汉词获取义原
    def getSememeByZh(self, word):

        if word in self.sememeindex_zn_.keys():
            return self.sememeindex_zn_[word]
        return None

    # 获取词汇表中的词
    def getGlossary(self, word):

        if isInGlossarytable_(self.glossarytable_.keys(), word):
            return valuesOfGlossarytable_(self.glossarytable_, word)
        return None

    # 计算词汇表中两个词的相似度
    def calcGlossarySim(self, w1, w2, BETA, GAMA, DELTA, ALFA):

        if w1 is None or w2 is None:
            return 0.0

        if w1.solid != w2.solid:
            return 0.0

        sim1 = self.calcSememeSimFirst(w1, w2, DELTA, ALFA)
        sim2 = self.calcSememeSimOther(w1, w2, GAMA, DELTA, ALFA)
        sim3 = self.calcSememeSimRelation(w1, w2, GAMA, DELTA, ALFA)
        sim4 = self.calcSememeSimSymbol(w1, w2, GAMA, DELTA, ALFA)

        # 计算公式
        sim = BETA[0] * sim1 + BETA[1] * sim1 * sim2 + BETA[2] * sim1 * sim2 * sim3 + BETA[3] * sim1 * sim2 * sim3 * sim4

        return sim

    # 计算两个义原之间的相似度
    def calcSememeSim(self, w1, w2, DELTA, ALFA):

        if empty(w1) and empty(w2):
            return 1.0
        if empty(w1) or empty(w2):
            return DELTA
        if w1 == w2:
            return 1.0

        d = self.calcSememeDistance(w1, w2)
        if d >= 0:
            return ALFA / (ALFA + d)
        else:
            return -1.0

    # 计算义原之间的距离(义原树中两个节点之间的距离)
    def calcSememeDistance(self, w1, w2):

        s1 = self.getSememeByZh(w1)
        s2 = self.getSememeByZh(w2)

        if s1 is None or s2 is None:
            return -1.0

        fatherpath = []
        id1 = s1.id
        father1 = s1.father

        while id1 != father1:
            fatherpath.append(id1)
            id1 = father1
            father_ = self.getSememeByID(father1)
            if father_:
                father1 = father_.father
        fatherpath.append(id1)

        id2 = s2.id
        father2 = s2.father
        len_ = 0.0
        fatherpathpos = []
        while id2 != father2:
            if id2 in fatherpath:
                fatherpathpos = fatherpath.index(id2)
                return fatherpathpos + len_

            id2 = father2
            father_ = self.getSememeByID(father2)
            if father_:
                father2 = father_.father
            len_ = len_ + 1.0

        if id2 == father2:
            if id2 in fatherpath:
                fatherpathpos = fatherpath.index(id2)
                return fatherpathpos + len_

        return 20.0

    # 计算第一基本义原之间的相似度
    def calcSememeSimFirst(self, w1, w2, DELTA, ALFA):

        return self.calcSememeSim(w1.s_first, w2.s_first, DELTA, ALFA)

    # 计算其他义原之间的相似度
    def calcSememeSimOther(self, w1, w2, GAMA, DELTA, ALFA):

        if w1.s_other == [] and w2.s_other == []:
            return 1.0
        sum_ = 0.0
        maxTemp = 0.0
        temp = 0.0
        for i in range(len(w1.s_other)):
            maxTemp = -1.0
            temp = 0.0

            for j in range(len(w2.s_other)):
                temp = 0.0
                if w1.s_other[i][0] != '(' and w2.s_other[j][0] != '(':
                    temp = self.calcSememeSim(w1.s_other[i], w2.s_other[j], DELTA, ALFA)

                elif w1.s_other[i][0] == '(' and w2.s_other[j][0] == '(':
                    if w1.s_other[i] == w2.s_other[j]:
                        temp = 1.0
                    else:
                        maxTemp = 0.0
                else:
                    temp = GAMA

                if temp > maxTemp:
                    maxTemp = temp

            if maxTemp == -1.0:
                maxTemp = DELTA

            sum_ = sum_ + maxTemp

        if len(w1.s_other) < len(w2.s_other):
            sum_ = sum_ + (len(w2.s_other) - len(w1.s_other)) * DELTA

        return sum_ / max(len(w1.s_other), len(w2.s_other))

    # 计算关系义原之间的相似度
    def calcSememeSimRelation(self, w1, w2, GAMA, DELTA, ALFA):

        if w1.s_relation == {} and w2.s_relation == {}:
            return 1.0

        sum_ = 0.0
        maxTemp = 0.0
        temp = 0.0

        for it1 in w1.s_relation.keys():
            maxTemp = 0.0
            temp = 0.0

            if it1 in w2.s_relation.keys():
                if w1.s_relation[it1][0] != '(' and w2.s_relation[it1][0] != '(':
                    temp = self.calcSememeSim(w1.s_relation[it1], w2.s_relation[it1], DELTA, ALFA)
                elif w1.s_relation[it1][0] == '(' and w2.s_relation[it1][0] == '(':
                    if w1.s_relation[it1] == w2.s_relation[it1]:
                        temp = 1.0
                    else:
                        maxTemp = 0.0
                else:
                    temp = GAMA
            else:
                maxTemp = DELTA

            if temp > maxTemp:
                maxTemp = temp

            sum_ = sum_ + maxTemp

        if len(w1.s_relation) < len(w2.s_relation):
            sum_ = sum_ + (len(w2.s_relation) - len(w1.s_relation)) * DELTA

        return sum_ / max(len(w1.s_relation), len(w2.s_relation))

    # 计算符号义原之间的相似度
    def calcSememeSimSymbol(self, w1, w2, GAMA, DELTA, ALFA):

        if w1.s_symbol == {} and w2.s_symbol == {}:
            return 1.0

        sum_ = 0.0
        maxTemp = 0.0
        temp = 0.0

        for it1 in w1.s_symbol.keys():
            maxTemp = 0.0
            temp = 0.0

            if it1 in w2.s_symbol.keys():
                if w1.s_symbol[it1][0] != '(' and w2.s_symbol[it1][0] != '(':
                    temp = self.calcSememeSim(w1.s_symbol[it1], w2.s_symbol[it1], DELTA, ALFA)
                elif w1.s_symbol[it1][0] == '(' and w2.s_symbol[it1][0] == '(':
                    if w1.s_symbol[it1] == w2.s_symbol[it1]:
                        temp = 1.0
                    else:
                        maxTemp = 0.0
                else:
                    temp = GAMA
            else:
                maxTemp = DELTA

            if temp > maxTemp:
                maxTemp = temp

            sum_ = sum_ + maxTemp

        if len(w1.s_symbol) < len(w2.s_symbol):
            sum_ = sum_ + (len(w2.s_symbol) - len(w1.s_symbol)) * DELTA

        return sum_ / max(len(w1.s_symbol), len(w2.s_symbol))

    # 计算两个词的语义相似度（返回值: [0, 1], -2:指定的词词典中不存在）
    def calc(self, w1, w2, BETA, GAMA, DELTA, ALFA):

        if w1 == w2:
            return 1
        sw1 = self.getGlossary(w1)  # glossary list
        sw2 = self.getGlossary(w2)
        if sw1 is None or sw2 is None or len(sw1) <= 0 or len(sw2) <= 0:
            return -2

        max__ = 0
        tmp = 0
        for i in range(len(sw1)):
            for j in range(len(sw2)):
                tmp = self.calcGlossarySim(sw1[i], sw2[j], BETA, GAMA, DELTA, ALFA)
                max__ = max(max__, tmp)

        return max__


if __name__ == '__main__':

    generatePlabel = True
    SIMILARITY = True

    if generatePlabel:
        glossaryfile = './hownet/glossary.dat'
        xiepeiyidic = './result/bt_xiepeiyiVerb.dic'
        lines = generateSourcefile(glossaryfile, xiepeiyidic)
        print('There are ' + str(len(lines)) + ' lines!!')

        if SIMILARITY:
            BETA = [0.5, 0.2, 0.17, 0.13]
            GAMA = 0.2
            DELTA = 0.2
            ALFA = 1.6

            sememefile = './hownet/whole.dat'
            glossaryfile = './hownet/glossary.dat'

            obj = WordSimilarity()

            if obj.init(sememefile, glossaryfile) is False:
                print("[ERROR] init failed!!")

            word1 = '时间'
            word2 = '地点'
            print word1, word2
            ciyu_sim = obj.calc(word1, word2, BETA, GAMA, DELTA, ALFA)
            print ciyu_sim

            # resultFile = './result/result.txt'
            # resultdic = {}
            # with open(resultFile, 'wt') as writer:
            #     for line in lines:
            #         l = line.split()
            #         word1 = l[0]
            #         word2 = l[1]
            #         print word1, word2
            #         sim = obj.calc(word1, word2, BETA, GAMA, DELTA, ALFA)
            #         print sim
                    # resultdic[line] = sim
                    # writer.write(line+'\t'+str(sim))
                    # print('[sim] %s - %s : %f\n' % (word1, word2, sim))
                # sorted by similarity
                # resultdic = sorted(resultdic.items(), key=lambda d: d[1], reverse=True)

                # write file
                # for key, value in resultdic:
                #     writer.write(key + '\t' + str(value))
