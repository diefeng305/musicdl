import os
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from musicdl import musicdl

app = Flask(__name__)

# 定义音乐保存路径
DOWNLOAD_DIR = os.getenv("MUSICDL_WORK_DIR", "/downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 支持的所有音乐平台源
ALL_SOURCES = [
    'NeteaseMusicClient', 'QQMusicClient', 'KugouMusicClient', 'KuwoMusicClient',
    'MiguMusicClient', 'QianqianMusicClient', 'SodaMusicClient', 'BilibiliMusicClient',
    'StreetVoiceMusicClient', 'XimalayaMusicClient', 'LanrenMusicClient', 'LizhiMusicClient',
    'QingtingMusicClient', 'JooxMusicClient', 'TidalMusicClient', 'YoutubeMusicClient',
    'AppleMusicClient', 'SpotifyMusicClient', 'QobuzMusicClient', 'SoundcloudMusicClient'
]

# 缓存最近一次搜索结果
SEARCH_CACHE = {}

@app.route('/')
def index():
    return render_template('index.html', sources=ALL_SOURCES)

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json or {}
    keyword = data.get('keyword', '').strip()
    sources = data.get('sources', [])
    search_size = int(data.get('search_size', 10))

    if not keyword:
        return jsonify({'success': False, 'message': '搜索关键词不能为空'}), 400

    if not sources:
        sources = ['NeteaseMusicClient', 'QQMusicClient', 'KugouMusicClient', 'KuwoMusicClient']

    # 配置各个平台的搜索及存储路径
    init_cfg = {}
    for src in sources:
        init_cfg[src] = {
            'work_dir': DOWNLOAD_DIR,
            'search_size_per_source': search_size
        }

    try:
        mc = musicdl.MusicClient(music_sources=sources, init_music_clients_cfg=init_cfg)
        results = mc.search(keyword=keyword)
        
        flat_results = []
        item_id = 0
        SEARCH_CACHE.clear()

        if isinstance(results, dict):
            for src_name, songs in results.items():
                for song in songs:
                    song_id = f"song_{item_id}"
                    item_id += 1
                    song_info = {
                        'id': song_id,
                        'source': src_name,
                        'title': song.get('songname', song.get('title', '未知歌名')),
                        'singers': song.get('singers', song.get('artist', '未知歌手')),
                        'album': song.get('album', '未知专辑'),
                        'ext': song.get('ext', 'mp3'),
                    }
                    SEARCH_CACHE[song_id] = {'client': mc, 'song': song}
                    flat_results.append(song_info)
        
        return jsonify({'success': True, 'results': flat_results, 'total': len(flat_results)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download():
    data = request.json or {}
    song_id = data.get('song_id')

    if not song_id or song_id not in SEARCH_CACHE:
        return jsonify({'success': False, 'message': '请先重新搜索后再点击下载'}), 400

    cache_item = SEARCH_CACHE[song_id]
    mc = cache_item['client']
    song_data = cache_item['song']

    def async_download():
        try:
            mc.download([song_data])
        except Exception as e:
            print(f"Download error: {e}")

    threading.Thread(target=async_download).start()
    return jsonify({'success': True, 'message': '后台正在下载，稍后可在下方下载列表中查看与下载！'})

@app.route('/api/files', methods=['GET'])
def list_files():
    files = []
    if os.path.exists(DOWNLOAD_DIR):
        for fname in os.listdir(DOWNLOAD_DIR):
            fpath = os.path.join(DOWNLOAD_DIR, fname)
            if os.path.isfile(fpath):
                files.append({
                    'name': fname,
                    'size': f"{os.path.getsize(fpath) / (1024*1024):.2f} MB"
                })
    return jsonify({'success': True, 'files': files})

@app.route('/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)