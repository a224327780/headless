import asyncio
import os
import random
import string

from pymongo import MongoClient

from libs.base import BaseClient

name_list = ["sleepm",
             "Leon6868", "whywhywhy", "chust", "lxl1531", "zoewendel", "fox233", "weifan", "iNaru",
             "Coeus999", "movq", "Contextualist", "Anderson997", "947", "chaleaoch", "cgqsidney",
             "leogoforit", "Claar",
             "netshell", "julyclyde", "blogfeng", "creatdate", "V9230", "zhoujinjing09", "dazkarieh",
             "python0707",
             "AlohaV2", "jerfoxu", "ljlljl0", "sagaxu", "delectate", "flowfire", "jaylee4869", "hp944244",
             "lengyihan",
             "123abcdf11345", "yuxi521", "louettagfh", "justNoBody", "sunyanfei", "zhuzhibin", "ligiggy",
             "VZXXBACQ",
             "levelworm", "meepo3927", "aweib000", "sillydaddy", "kely", "Roxk", "PerFectTime", "cyhah9736",
             "redtree",
             "Maxxxxyu", "chendy", "webmastere", "razios", "zjuster", "xwcs", "0kaka", "fidetro",
             "PepperEgg", "Menci",
             "mrsupns", "jim9606", "ccxykey", "idragonet", "defunct9", "redwing2003", "ye4tar", "lambdaq",
             "joudev",
             "yujiang", "forgottencoast", "getYourMother", "zuihoudezhanyi", "naoh1000", "jwenjian",
             "v2tudnew",
             "hqweay",
             "gftfl", "NilChan", "polyang", "zshstc", "zanrenXu", "chrisia", "jones2000", "labulaka521",
             "tatacheung",
             "taobibi", "james504", "LeeReamond", "GrayXu", "ward56", "Geel", "ubuntuGary", "SaoHe",
             "darknoll",
             "ByteCat",
             "redial39", "jasonkayzk", "NekoTMG", "xushuangnet", "xiqian", "hbxsdfx", "ysicing", "junweigu",
             "Play1",
             "360511404", "yzql2018", "yeeyeung", "zyb201314", "tlerbao", "bear2000", "justin2018",
             "Plague", "otokaze",
             "yangwcool", "kele1997", "delores6", "YoungChan", "chinesedragon", "msg7086", "zzzrf",
             "SunspotsInys",
             "nanmu42", "hillMonkey", "awanganddong", "ro47bot", "nl101531", "lixuda", "RedBeanIce",
             "moonkiller",
             "YUX",
             "lenghonglin", "robotkang1", "hupo0", "ClericPy", "wakzz", "chenyu0532", "GoLand", "zzx0403",
             "gBurnX",
             "happyss", "ccraohng", "imn1", "hdp5252", "lycongtou", "cuppuccino", "James369", "daimaosix",
             "dvaknheo",
             "cenbiq", "pytth", "unco020511", "alexnapolun", "icetea12138", "alfchin", "lugegege",
             "smqk2020", "uadw",
             "SummerSec", "100calorie", "hzm0318hzm", "ClutchBear", "CoderLife", "Privileges", "qoras",
             "mitsuizzz",
             "120qwer", "kangism", "PeakFish", "iyg429", "UnknownSky", "ambeta", "TigerGod", "qazsewong",
             "css3",
             "Blessing1", "java8", "sadhen", "YOKAMIA", "snimstice", "cesar", "proxychains", "stillsilly",
             "dorothyREN",
             "iceteacover", "bandian", "cco", "soooulp", "Mahayu", "unbeau", "codists", "miv", "luckyrayyy",
             "becauseOf",
             "manchen0528", "shanex", "Meiyun", "xuegy", "orangy", "lowkey1337", "KennyMcCormick",
             "applehater", "Exin",
             "shunlongyang", "youlemei", "jobs0", "Newyorkcity", "zkhhkz123", "KrisLiu", "revival83",
             "MakeItGreat",
             "exc",
             "suzper", "secretman", "woshichuanqilz", "WillBC", "JustSong", "bitholic", "SaberAlter",
             "rayliao",
             "CivAx",
             "shenjialun", "zanyfly", "chenggiant", "yazoox", "andy2018", "EEEcho", "nalzok", "KEYIIIII",
             "calmzhu",
             "samyao99", "spark2Fire", "latiao", "vashthewhite", "iAndychan", "sbilly", "sinmu",
             "yestodayHadRain",
             "IDAEngine", "hantsy", "fz420", "oakcdrom", "piqizhu8", "raincode", "Leronron", "AlkTTT",
             "Smash", "ff520",
             "zhuoyi", "suueyoung", "yunyuyuan", "LittleDeng", "johncang", "AlwaysCGG", "Apol1oBelvedere",
             "whrssl",
             "dadachen1997", "rinima", "mokevip", "helloworld2076", "patagonia111010", "iscurry", "peterlu",
             "ferock",
             "lc7029", "Shook", "xlsama", "no1xsyzy", "shgdym", "Orciorc", "brendan", "ruimz", "pjntt",
             "joest",
             "HashV2",
             "cnbattle", "ChrisZou", "freemana", "qazwsxkevin", "lbllol365", "axeprpr1", "cody1991",
             "aero99",
             "fullstop1005", "systemcall", "omph", "yhan", "TophTab", "Regened", "mdemo", "supremacyxxxxx",
             "learningmachine", "DaimHin", "zzq825924", "yylts", "zhucelws", "iamv2er", "nomeguy",
             "eason1874", "fyovo",
             "Apple2023", "ciyuev", "seven123", "Altale", "LukeChien", "geebos", "fateofheart", "zhangrh",
             "bclerdx",
             "xuweifeng1987", "ryan2333", "remiver", "01802", "blackbookbj", "Yoock", "lmh19941113",
             "KouShuiYu",
             "dot2017",
             "miyunda", "xx6412223", "Aaron55", "lakie", "BahuangShanren", "emric", "l195817355",
             "zhoudaiyu",
             "shniubobo",
             "justs0o", "XJohn", "windyCity1", "lj0014", "lau52y", "yagamil", "misaki321", "mincoke",
             "hooopo", "rshun",
             "airyland", "onice", "itsql", "horseInBlack", "lcc142625", "msn1983aa", "shanmin", "hotlook10",
             "cxp",
             "wangkun025", "amiwrong123", "faustina2018", "yanzhiling2001", "fangxiaoning", "liuxu",
             "wmwmajie",
             "Sparkli",
             "SherloFun", "dongdawang", "JLTHU", "chenqh", "j165287", "chenjieshou", "adoontheway",
             "BBrother",
             "xiangbudaomingzi", "ashuai"]


class ShutterFly(BaseClient):

    def __init__(self):
        super().__init__()
        self.url = 'https://accounts.shutterfly.com/signup'
        self.email_list = ['web01.ml', 'demo666.cn', 'mail01.tk', 'mail02.tk', 'huxiang.onmicrosoft.com']

    async def handler(self, **kwargs):
        mongo_uri = os.environ.get('MONGO_URI')
        client = MongoClient(mongo_uri, connectTimeoutMS=5000, socketTimeoutMS=5000)
        db = client.get_database('db0')
        col = db['shutterfly']

        n = ''.join(random.choices(string.digits, k=2))
        self.username = f'{random.choice(name_list)}{n}'
        email_suffix = random.choice(self.email_list)
        email = f'{self.username}@{email_suffix}'
        try:
            self.logger.info(f'{self.username} start signup.')
            await asyncio.sleep(5)
            await self.page.type('#firstName', ''.join(random.choices(string.ascii_lowercase, k=3)), {'delay': 30})
            await asyncio.sleep(0.5)
            await self.page.type('#lastName', ''.join(random.choices(string.ascii_lowercase, k=3)), {'delay': 30})
            await asyncio.sleep(0.5)
            await self.page.type('#email', email, {'delay': 30})
            await asyncio.sleep(0.5)
            await self.page.type('#confirmEmail', email, {'delay': 30})
            await asyncio.sleep(0.5)
            await self.page.type('#password', self.password, {'delay': 30})
            await asyncio.sleep(0.5)
            await self.page.click('#signUpButton')
            await asyncio.sleep(8)

            if self.url != self.page.url:
                self.logger.info(f'{self.username} register done.')
                col.update_one({'_id': email}, {'$set': {'password': self.password}}, True)
        except Exception as e:
            self.logger.exception(e)
        finally:
            client.close()
