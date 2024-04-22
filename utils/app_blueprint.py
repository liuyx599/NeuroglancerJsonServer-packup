# g 是一个特殊的全局对象，被称为 "Application Context Globals"（应用程序上下文全局对象）
from flask import Blueprint, request, make_response, jsonify, g
from flask import current_app
from flask import  abort
import json
import time
import datetime

from . import database

bp = Blueprint('neuroglancerjsonserver', __name__, url_prefix="/nglstate")
__version__ = "0.2.12"
# -------------------------------
# ------ Access control and index
# -------------------------------


# 访问 http://localhost:5000/nglstate/  页面显示  NeuroglancerJsonServer - version 0.2.12
@bp.route('/', methods=["GET"])
@bp.route("/index", methods=["GET"])
def index():
    return "NeuroglancerJsonServer - version " + __version__   # html的内容，这里应该也可以用html什么的修饰

@bp.route
def home():
    # 创建响应头
    resp = make_response()
    resp.headers['Access-Control-Allow-Origin'] = '*'
    acah = "Origin, X-Requested-With, Content-Type, Accept"
    resp.headers["Access-Control-Allow-Headers"] = acah
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    resp.headers["Connection"] = "keep-alive"
    return resp

# -------------------------------
# ------ Measurements and Logging
# -------------------------------
# Flask中间件
# NEW REQUEST: 2023-10-22 22:07:58.819981 http://localhost:5000/nglstate/
# Response time: 0.998ms

# bp是Blueprint（蓝图）的缩写。蓝图是一种组织和管理路由、视图函数和静态文件等的方式
@bp.before_request
def before_request():
    print("NEW REQUEST:", datetime.datetime.now(), request.url)
    g.request_start_time = time.time()


@bp.after_request
def after_request(response):
    dt = (time.time() - g.request_start_time) * 1000

    url_split = request.url.split("/")
    current_app.logger.info("%s - %s - %s - %s - %f.3" %
                            (request.path.split("/")[-1], "1",
                             "".join([url_split[-2], "/", url_split[-1]]),
                             str(request.data), dt))

    print("Response time: %.3fms" % (dt))
    return response


@bp.errorhandler(500)
def internal_server_error(error):
    dt = (time.time() - g.request_start_time) * 1000

    url_split = request.url.split("/")
    current_app.logger.error("%s - %s - %s - %s - %f.3" %
                             (request.path.split("/")[-1],
                              "Server Error: " + error,
                              "".join([url_split[-2], "/", url_split[-1]]),
                              str(request.data), dt))
    return 500




@bp.errorhandler(Exception)
def unhandled_exception(e):
    dt = (time.time() - g.request_start_time) * 1000

    url_split = request.url.split("/")
    current_app.logger.error("%s - %s - %s - %s - %f.3" %
                             (request.path.split("/")[-1],
                              "Exception: " + str(e),
                              "".join([url_split[-2], "/", url_split[-1]]),
                              str(request.data), dt))
    return 500

# -------------------
# ------ Applications
# -------------------

# 设置数据库
# 如果是SQLite 请将neuroglancerjsonserve/jsonserve.db复制到当前目录下
def get_db():
    if 'db' not in g:
        # g.db = database.JsonDataBaseMySQL()
        g.db = database.JsonDataBaseSQLite()
    return g.db



@bp.errorhandler(404)
def not_found_error(error):
    dt = (time.time() - g.request_start_time) * 1000

    url_split = request.url.split("/")
    current_app.logger.error("%s - %s - %s - %s - %f.3" %
                             (request.path.split("/")[-1],
                              "Server Error: " + str(error),
                              "".join([url_split[-2], "/", url_split[-1]]),
                              str(request.data), dt))
    return jsonify(message="Not Found"), 404


@bp.route('/<json_id>', methods=['GET'])
def get_json(json_id):
    db = get_db()

    json_data = db.get_json(int(json_id), decompress=True)

    if json_data is None:
        abort(404)  # 触发 404 错误
    else:
        return jsonify(json.loads(json_data))


@bp.route('/raw/<json_id>', methods=['GET'])
# @auth_required  #不需要认证
def get_raw_json(json_id):
    db = get_db()

    json_data = db.get_json(int(json_id), decompress=False)

    return json_data


@bp.route('/post', methods=['POST', 'GET'])
# @auth_required
def add_json():
    db = get_db()

    json_id = db.add_json(request.data)

    url_base = request.url.strip("/").rsplit("/", 1)[0]

    print("\n\n\n\n")
    print(url_base)
    print(json_id)
    print("{}/{}".format(url_base, json_id))
    print(jsonify("{}/{}".format(url_base, json_id)))
    print("\n\n\n\n")

    return jsonify("{}/{}".format(url_base, json_id))
