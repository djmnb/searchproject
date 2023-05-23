

# 用于存放一些常量
# 100 以内为了一些状态码
# 1xx 为一些类型代码
# 2xx 为成功
# 4xx 为客户端错误
# 5xx 为系统错误


USER_NORMAL = True                    #账号正常
USER_BAN = False                      #账号被封禁

ALL_QUESTION = "ALL_QUESTION"       #所有问题
MY_QUESTION = "MY_QUESTION"         #我的问题
SINGEL_QUESTION = "SINGEL_QUESTION" #单个问题


CODE_REGISTER = 100                 # 注册
CODE_CHANGE_PASSWORD = 101          # 修改密码
CODE_FORGET_PASSWORD = 102          # 忘记密码

IS_OK = 200                         # 成功
 
 
USER_NOT_LOGIN = 400                # 没有登录,没有权限访问页面
MISSING_PARAMETER = 401             # 缺少请求参数
DATA_FORMAT_ERROR = 402             # 数据格式错误
PARAM_ERROR = 403                   # 参数错误
NOT_FOUND = 404                     # 请求不存在
QUESTION_NOT_FOUND = 405            # 题目不存在
USER_NOTFOUND = 406                 # 用户不存在
PAGE_NOT_FOUND = 407                # 页码不存在
NOT_ENOUGH = 408                    # 余额不足
PASSWORD_NOT_MATCH = 409            # 密码不一致
PASSWORD_ERROR = 410                # 密码错误
USER_EXIST = 411                    # 用户已经存在
CODE_ERROR = 412                    # 验证码不正确
EMAIL_NOT_VALID = 413               # 邮箱不合法
FILE_LAGER_THAN_5M = 414            # 文件大于5M

SERVER_ERROR = 500                  # 服务器错误

PICTRURE_ERROR = 508                # 图片识别出现错误




