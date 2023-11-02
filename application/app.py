from flask import Flask
from flask import jsonify, request
from pytube import YouTube
from redis import Redis

class MiniRedis(Redis):

    def __init__(self, host, port):
        super().__init__(host=host, port=port)

    def turn_on(self, channel: str):
        self.lpush(channel, 1)    

    def turn_off(self, channel: str):
        self.lpush(channel, 0)    

    def check(self, channel: str):
        return bool(int(str(redis.lindex('download', 0), "utf-8")))
        
app = Flask(__name__)
redis = MiniRedis(host='application-redis', port=6379)
redis.turn_on("download")


@app.route('/')
def index():
    download_state = redis.check("download")
    return f"""
        <p><b>DOWNLOAD: </b>
            <button 
                type="button" 
                style="background-color: {"lightgreen" if download_state else "red"}">
                {"Available" if download_state else "Not Available"}
            </button>
        </p>
    """

@app.route('/api/v1/download', methods=["GET"])
def download():
    url = request.args.get("url", None)

    redis.turn_off("download")
    video = YouTube(url).streams.first().download()
    redis.turn_on("download")
    return jsonify({
        "application": {
            "DOWNLOAD": "Completed"
            }
        })

@app.route('/api/v1/ping')
def ping():
    environment_state = {}
    redis_status = redis.ping()
    return jsonify({
        "application": {
            "REDIS": redis_status,
            "DOWNLOAD": "Available" if redis.check("download") else "Not Available"
            }
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)