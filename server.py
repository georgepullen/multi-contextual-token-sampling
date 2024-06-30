from flask import Flask, request, jsonify
from flask_cors import CORS

from inference import create_response
from log_system import apply_filter

app = Flask(__name__)
CORS(app)


@app.route('/')
async def respond_as_agent():
    prompt = request.args.get('prompt')
    username = request.args.get('username')
    group_users = request.args.getlist('group_users')

    filtered_username = await apply_filter(username)
    filtered_group_users = [await apply_filter(user) for user in group_users]

    filtered_prompt = await apply_filter(prompt)
    filtered_prompt = '\n' + f'{filtered_username} said, "{filtered_prompt}" agent replied, "'

    response = await create_response(filtered_prompt, filtered_username, filtered_group_users)
    
    return jsonify({
        'response': f'{response}'
    })

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)
