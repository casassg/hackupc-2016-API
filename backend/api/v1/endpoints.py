from flask import Blueprint, request, abort
import uuid
# import datetime
from decorators import asJSON, requiresToken, requiresAdmin
from typeform import getMoreResponses
import hashlib
from models.judge import Judge
from models.application import Application
import random
from models.judgement import Judgement
from models.db import db
from sqlalchemy import desc, asc

apiv1 = Blueprint('apiv1', __name__)

# AUTH LOGIN
# GET /api/v1/login
@apiv1.route('/api/v1/login', methods=['POST'])
@asJSON
def login_user():
    login_data = request.get_json()
    username = login_data['user']
    pwd = hashlib.sha512(login_data['password']).hexdigest()

    user = Judge.query.filter_by(name=username, password=pwd).first()
    if user is not None:
        token = str(uuid.uuid4())
        user.token = token
        db.session.commit()
        return {'token': token, 'admin': user.admin}
    else:
        abort(403)


# GET ALL APPLICANTS
# GET /api/v1/applicants
@apiv1.route('/api/v1/applicants', methods=['GET'])
@requiresToken
@asJSON
def get_applicants():
    applications = Application.query.all()
    applications_json = []
    for app in applications:
        applications_json.append(app.to_dict())

    return applications_json


# GET LAST JUDGED APPLICATION
# GET /api/v1/application/last
@apiv1.route('/api/v1/application/last', methods=['GET'])
@requiresToken
@asJSON
def get_last_application():
    id = Judge.getJudgeIdByToken()

    judgement = Judgement.query\
        .filter_by(judge_id=id, )\
        .filter(Judgement.rating != '')\
        .order_by(desc(Judgement.judge_index))\
        .first()

    if judgement is None:
        return {}

    app_id = judgement.app_id

    app = Application.query.filter_by(id=app_id).first()
    return app.to_dict()

# GET NEXT APPLICATION TO JUDGE
# GET /api/v1/application/next
@apiv1.route('/api/v1/application/next', methods=['GET'])
@requiresToken
@asJSON
def get_next_application():
    id = Judge.getJudgeIdByToken()
    needs_new_judgement = True
    app = None

    #Get current application being judged
    current = Judgement.getCurrentJudgementByJudgeId(id)
    if current:
        app_id = current.app_id
        app = Application.query.filter_by(id=app_id).first()
        needs_new_judgement = app.state != 'tbd'

    if needs_new_judgement:
        judge_judgements = Judgement.query.filter_by(judge_id=id).all()
        apps_judged = set([judge_judgement.app_id for judge_judgement in judge_judgements])
        apps_all = set([application[0] for application in Application.query.filter_by(state='tbd').values('id')])
        apps_missing = apps_all - apps_judged
        if not apps_missing:
            return {'status':'everyone_judged'}
        app_id = random.sample(apps_missing,1)[0]
        newJudgement = Judgement(app_id=app_id, judge_id=id)
        newJudgement.judge_index = len(judge_judgements)
        newJudgement.rating = ''
        db.session.add(newJudgement)
        db.session.commit()
        app = Application.query.filter_by(id=app_id).first()

    if app is not None:
        return app.to_dict()
    else:
        return {}

# RATE AN APPLICATION
# POST /api/v1/rate/<rating>
@apiv1.route('/api/v1/rate/<rating>', methods=['POST'])
@requiresToken
@asJSON
def rate_application(rating):
    id = Judge.getJudgeIdByToken()
    judgement = Judgement.getCurrentJudgementByJudgeId(id)

    if judgement is None:
        return {"status": "ko"}

    judgement.rating = rating
    db.session.commit()

    return {"status": "ok"}

# CHANGE STATE OF APPLICATION
# POST /api/v1/state/<int:application_id>/<state>
@apiv1.route('/api/v1/state/<int:application_id>/<state>', methods=['POST'])
@requiresToken
@requiresAdmin
@asJSON
def change_application_state(application_id, state):
    app = Application.query.filter_by(id=application_id).first()

    if app is not None:
        app.state = state
        db.session.commit()
        return {"result": "ok"}

    return {"result": "ko"}  

# GET APPLICATION DETAIL
# POST /api/v1/application/<int:application_id>
@apiv1.route('/api/v1/application/<int:application_id>', methods=['GET'])
@requiresToken
@asJSON
def get_application_detail(application_id):
    app = Application.query.filter_by(id=application_id).first()

    if app is not None:
        return app.to_dict()
    else:
        abort(404)


# GET /api/v1/fetch
@apiv1.route('/api/v1/fetch', methods=['GET'])
@asJSON
def fetch_responses():
    getMoreResponses()
    return {"result": "ok"}
