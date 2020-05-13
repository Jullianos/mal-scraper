from pymediainfo import MediaInfo
import json

media_info = MediaInfo.parse('Episode 1.mkv')

print(type(media_info))

for track in media_info.tracks:
    data = track.to_data()
    json_data = json.dumps(data)
    print(json_data)
    # for k, v in data:
    #     print(k)
    #     print(f'\t{str(v)}')

    # print(track.to_data())
