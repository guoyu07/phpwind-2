# coding:utf-8
import re
import time
import urllib
import urllib2
import cookielib
class phpwind():
    def __init__(self,url,username,password,jumpurl=""):
        self.host=url
        self.username=username
        self.password=password
        self.hash=re.findall("var verifyhash = '.*?';",urllib.urlopen(self.host).read())[0][18:-2]
        self.loginurl=self.host+"/login.php?nowtime="+self.getCurrentTime()+"&verify=%s"%self.hash
        self.siginurl=self.host+'/u.php'
        self.siginsss=self.host+("/jobcenter.php?action=punch&verify=%s&nowtime="+self.getCurrentTime()+"&verify=%s")%(self.hash,self.hash)
        self.jumpurl =jumpurl
        if self.jumpurl=='':
            self.jumpurl=self.host+"/index.php"
        self.cookie=cookielib.CookieJar()
        self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
    # 获取当前时间
    @staticmethod
    def getCurrentTime():
        return str(time.time()).replace('.','')+'0'
    # 登陆 返回值为布尔类型
    def login(self):
        postdata = urllib.urlencode({
            'ajax': '1',
            'cktime': '31536000',
            'jumpurl': self.jumpurl,
            'lgt': '0',
            'pwpwd': self.password,
            'pwuser': self.username,
            'step': '2'
        })
        self.opener.open(self.loginurl, postdata)
        result=self.opener.open(self.jumpurl)
        if len(re.findall("var windid	= '"+self.username+"';",result.read())):
            self.hash=re.findall('var verifyhash = \'.*?\';',self.read(self.host))[0].split("'")[1]
            # print "login secuss"
            return True
        # print "login faild"
        return False
    # 带cookie读取页面吧
    def read(self,url):
        return self.opener.open(url).read().decode('gbk').encode('utf-8')
    # 判断是否签到 返回值布尔类型
    def isSigin(self):
        if "每日打卡" in self.opener.open(self.siginurl).read().decode('gbk').encode('utf-8'):
            return False
        return True
    # 签到 返回值布尔类型
    def sigin(self):
        postdata = urllib.urlencode({
            'step': '2'
        })
        if "你已经打卡,请明天再试" in self.opener.open(self.siginsss, postdata).read().decode("gbk").encode("utf-8"):
            return True
        return False
    # 获取版块帖子 返回值为列表
    def getCard(self,fid,page):
        result=[]
        for x in re.findall('<a href=".*?" name="readlink" id=".*?" class="subject_t f14">[\w\W]*?</a>',self.read('http://bbs.mydigit.cn/thread.php?fid='+str(fid)+'&search=all&page='+str(page))):
            result.append((x.split('"')[1],x.split('"')[-1][1:-4]))
        return result
    # 添加关注 添加成功为True，无法判断成功返回服务器字符串
    def addFollow(self, uid):
        result = self.read('http://bbs.mydigit.cn/pw_ajax.php?action=addattention&touid=' + str(uid) + '&recommend=1&nowtime=' + self.getCurrentTime() + '&verify=' + self.hash)
        if 'success' in result:
            return True
        if '不存在' in result:
            return False
        return result
    # 加好友 添加成功为True，无法判断成功返回服务器字符串
    def addFriend(self,uid):
        postdata=urllib.urlencode({
            'verify'     : self.hash,
            'job'        : 'add',
            'step'       : '2',
            'touid'      : uid,
            'reload'     : '1',
            'checkmsg'   : '',
            'friendtype' : '0',
            'typename'   : ''
        })
        result = self.opener.open('http://bbs.mydigit.cn/pw_ajax.php?action=addfriend&nowtime='+self.getCurrentTime()+'&verify='+self.hash,postdata).read().decode('gbk').encode('utf-8')
        if '请求添加为好友，正在等待好友验证' in result:
            return True
        return result
    # 发送消息 返回服务器字符串
    def sendMessage(self,username,title,text):
        postdata=urllib.urlencode({
            'verify':self.hash,
            'step':'2',
            'pwuser':username,
            'msg_title':title.decode('utf-8').encode('gbk'),
            'atc_content':text.decode('utf-8').encode('gbk')
        })
        result = self.opener.open('http://bbs.mydigit.cn/pw_ajax.php?action=msg&nowtime=' + self.getCurrentTime() + '&verify=' + self.hash,postdata).read().decode('gbk').encode('utf-8')
        return result
    # 通过id获取用户名 用户不存在为False，存在为用户名
    def getNameById(self, uid):
        try:
            return re.findall('<strong class="f14 b">[\w\W]*?</strong>',self.read('http://bbs.mydigit.cn/u.php?uid='+str(uid)))[0][22:-9]
        except:
            return False
    # 取帖子回复数阅读数，刷沙发专用
    def getReplyAndRead(self,turl):
        html=self.read(self.host+'/' + turl)
        reply=re.findall('<em id="topicRepliesNum">.*?</em>',html)[0][25:-5]
        read=re.findall('<li><em>.*?</em>阅读</li>',html)[0][8:-16]
        return int(reply),int(read)
    # 回复帖子 能判断就为true，判断失败返回服务器字符串
    def reply(self,addr,text):
        if self.host not in addr:
            addr=self.host+'/'+addr
        html=self.read(addr)
        hexie,verify,fid,title=self.getHiddenInfo(html)
        postdata = urllib.urlencode({
            '_hexie'      : hexie,
            'action'      : 'reply',
            'ajax'        : '1',
            'atc_autourl' : '1',
            'atc_content' : str(text).decode('utf-8').encode('gbk'),
            'atc_convert' : '',
            'atc_title'   : '',
            'atc_usesign' : '1',
            'cyid'        : '',
            'fid'         : fid,
            'iscontinue'  : '0',
            'isformchecked': '1',
            'step'        : '2',
            'stylepath'   : 'wind',
            'tid'         : addr.split('tid')[1].split('&')[0].split('=')[1],
            'type'        : 'ajax_addfloor',
            'usernames'   : '',
            'verify'      : verify
        })
        repurl=self.host+'/post.php?fid='+str(fid)+'&nowtime='+self.getCurrentTime()+'&verify='+verify
        repdata=self.opener.open(repurl, postdata).read().decode('gbk').encode('utf-8')
        # return text in self.opener.open(reputl, postdata).read().decode('gbk').encode('utf-8')
        return True if len(repdata)>1000 or '<?xml version="1.0" encoding="gbk"?><ajax><![CDATA[]]></ajax>' in repdata else repdata
        # return self.opener.open(reputl, postdata).read().decode('gbk').encode('utf-8')
    # 获取回复需要隐藏参数
    def getHiddenInfo(self,html):
        string= re.findall('<h1 id="subject_tpc" class="read_h1"><a href="[\w\W]*?" class="s5">[\w\W]*?</h1>',html)[0]
        fid   = string.split('"')[5].split('?')[1].split('fid')[-1].split('=')[1].split('&')[0]
        title = string.split('</a>')[1].split("<a")[0]
        hexie = re.findall("document.FORM._hexie.value = '.*?';",html)[0].split("'")[1]
        verify= re.findall('<input type="hidden" value=".*?" name="verify">',html)[0].split('"')[3]
        return hexie,verify,fid,title
    # 评分 返回值布尔类型
    def score(self,addr,text,num=1 ,reply=True):
        if self.host not in addr:
            addr=self.host+'/'+addr
        html=self.read(addr)
        verify=re.findall('<input type="hidden" value=".*?" name="verify">',html)[0].split('"')[3]
        postdata = urllib.urlencode({
            'addpoint[]'  : str(num),
            'atc_content' : str(text).decode('utf-8').encode('gbk'),
            'cid[]'       : 'money',
            'ifpost'      : '1' if reply else '0',
            'page'        : '1',
            'selid[]'     : 'tpc',
            'step'        : '1',
            'tid'         : addr.split('tid')[1].split('&')[0].split('=')[1],
            'verify'      : verify
        })
        repurl = self.host+'/operate.php?action=showping&ajax=1&nowtime='+self.getCurrentTime()+'&verify='+verify
        repdata = self.opener.open(repurl, postdata).read().decode('gbk').encode('utf-8')
        return 'success' in repdata
    # 打印站点信息
    def pinfo(self):
        print  '====================================='
        print  '站点名称: %s'%re.findall("<title>.*?</title>",self.read(self.host))[0][7:-8]
        print  '用户: %s %s'%(self.username,"已经签到" if self.isSigin() else "并没有签到")
        for x in re.findall("<li>.{1,8}:.{1,16}</li>",self.read(self.host)):
            print x[4:-5]
        print  '====================================='


# '''http://bbs.mydigit.cn/jobcenter.php?action=punch&verify=1849a44a&nowtime=1475251499535&verify=1849a44a'''
a=phpwind("http://bbs.mydigit.cn","username",'password')
if a.login():
    a.pinfo()
    print a.getNameById(123)
    # for x in xrange(1400000,1600000):
    #     info=a.addFollow(uid=x)
    #     print info
    # 评分，参数为  地址 评论文本 评分 是否作为回复
    # print a.score('http://bbs.mydigit.cn/read.php?tid=1964462','厉害了我的小程序',1,True)
    # print a.reply('http://bbs.mydigit.cn/read.php?tid=1963796','回复字数长度不能太少')
    # a.getCard(137,1) 这个是获取137版块的第一页  http://bbs.mydigit.cn/thread.php?fid=137&search=all 这个就是137版块，fid就是版块的号码
    for page in xrange(2,500):
        for addr,title in a.getCard(85,page)[1:]:
            print addr,title,a.reply(addr,title)
            time.sleep(16)
            # reply,read=a.getReplyAndRead(addr)
            # if reply==0:
            #     print addr,title,a.reply(addr,title)
            #     time.sleep(16)  # 十五秒防水
            # print addr,title,reply,read
