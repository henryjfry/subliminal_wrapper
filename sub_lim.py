import os
import glob
import sys
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Subliminal'))
#import tools 

#cache_directory = tools.ADDON_USERDATA_PATH
def get_subs_file(cache_directory=None, video_path = None, same_folder=True):
	import subliminal
	from babelfish import Language
	from subliminal import download_best_subtitles, region, save_subtitles, scan_videos, Video, list_subtitles, compute_score, download_subtitles
	from subliminal import refiners
	import requests
	
	if cache_directory == None:
		print('NO CACHE DIRECTORY PROVIDED')
		return None, None
	if cache_directory == None:
		print('NO CACHE DIRECTORY PROVIDED')
		return None, None

	temp_directory = os.path.join(cache_directory,'temp')
	if not os.path.exists(cache_directory):
		os.mkdir(temp_directory)
	if not os.path.exists(temp_directory):
		os.mkdir(temp_directory)
	else:
		files = glob.glob(os.path.join(temp_directory,'*'))
		for f in files:
			os.remove(f)
	cache_file = os.path.join(cache_directory,'cachefile.dbm')

	with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.json')) as f:
		credentials_dict = eval(f.read())
	
	opensubtitlescom_credentials = {'username': credentials_dict['opensubtitles_com_username'], 'password': credentials_dict['opensubtitles_com_password']}
	opensubtitles_credentials = {'username': credentials_dict['opensubtitles_org_username'], 'password': credentials_dict['opensubtitles_org_password']}


	# configure the cache
	region.configure('dogpile.cache.dbm', arguments={'filename': cache_file})

	import subs_hash

	file_path = video_path

	from urllib.parse import unquote

	dir_source = None
	if not os.path.isfile(file_path):
		#use a temp folder where file isnt a file, eg a url
		same_folder = False
		MBFACTOR = float(1 << 20)
		response = requests.head(file_path, allow_redirects=True)
		size = response.headers.get('content-length', 0)
		file_path = unquote(file_path)
		size = int(size)
		#'hashes': {'opensubtitles': 'e45d225d49846408', 'opensubtitlescom': 'e45d225d49846408'}
		http_file = True
		returnedhash, filesize = subs_hash.hashFile_url(file_path)
		#print(returnedhash, filesize)
		hashes = {'opensubtitles': returnedhash, 'opensubtitlescom': returnedhash}
	else:
		dir_source =  os.path.dirname(file_path)
		size = os.stat(file_path).st_size
		http_file = False
		returnedhash, filesize = subs_hash.hashFile_url(file_path)
		#print(returnedhash, filesize)
		hashes = {'opensubtitles': returnedhash, 'opensubtitlescom': returnedhash}

	subs_out = os.path.basename(file_path)
	subs_out_FORCED = os.path.splitext(subs_out)[0] + str('.FOREIGN.PARTS.srt')
	subs_out_ENG = os.path.splitext(subs_out)[0] + str('.ENG.srt')

	if same_folder == True:
		out_directory = dir_source
	else:
		out_directory = temp_directory

	video = Video.fromname(file_path)
	#if not http_file:
	#	video = refiners.hash.refine(video, providers=['opensubtitles','addic7ed','napiprojekt','opensubtitlescom','podnapisi','tvsubtitles'],languages={Language('eng')})

	video = refiners.tmdb.refine(video, apikey=credentials_dict['tmdb_api'])

	video.__dict__['size'] = filesize
	video.__dict__['hashes'] = hashes

	"""
	{'name': '/folder/folder/file_path.mp4', 'source': 'Blu-ray', 'release_group': 'RARBG', 'streaming_service': None, 'resolution': '720p', 'video_codec': 'H.264', 'audio_codec': 'AAC', 'frame_rate': None, 'duration': None, 'hashes': {}, 'size': None, 'subtitles': set(), 'title': 'Movie Title', 'year': 2021, 'country': None, 'imdb_id': None, 'tmdb_id': None, 'alternative_titles': []}
	"""
	print(video.__dict__)
	
	#video.__dict__['episodes'] = [6]

	subtitles = list_subtitles([video], languages={Language('eng')}, providers=['opensubtitles','addic7ed','napiprojekt','opensubtitlescom','podnapisi','tvsubtitles'],	provider_configs={'opensubtitlescom': opensubtitlescom_credentials, 'opensubtitles': opensubtitles_credentials})

	print(subtitles[video])
	high_score_forced = 0
	high_score = 0
	curr_subs_forced = None
	curr_subs = None
	for i in subtitles[video]:
		if 'parts' in str(i.__dict__) or 'foreign' in str(i.__dict__):
			curr_score_forced = compute_score(i, video)
			if curr_score_forced > high_score_forced:
				high_score_forced = curr_score
				curr_subs_forced = i
				curr_subs_forced_dict = i.__dict__
		if not ('parts' in str(i.__dict__) or 'foreign' in str(i.__dict__)) and not 'HEARING' in str(i.__dict__):
			curr_score = compute_score(i, video)
			if curr_score > high_score:
				high_score = curr_score
				curr_subs = i
				curr_subs_dict = i.__dict__
	if curr_subs_forced:
		print(curr_subs_forced_dict)
		print(os.path.join(curr_subs_forced_dict['page_link'], curr_subs_forced_dict['filename']))
		download_subtitles([curr_subs_forced])
		file_type =  os.path.splitext(curr_subs_forced_dict['filename'])[1]
		subs_out_FORCED = subs_out_FORCED.replace('.srt',file_type)
		subs_out_FORCED = os.path.join(out_directory, subs_out_FORCED)
		with open(subs_out_FORCED, 'w', encoding='utf-8') as f:
			f.write(curr_subs_forced.text)
		if file_type == '.ass':
			subs_hash.ass_to_srt(subs_out_FORCED, subs_out_FORCED.replace(file_type,'.srt'))
			subs_out_FORCED = subs_out_FORCED.replace(file_type,'.srt')
	else:
		subs_out_FORCED = None

	if curr_subs:
		print(curr_subs_dict)
		print(os.path.join(curr_subs_dict['page_link'], curr_subs_dict['filename']))
		file_type =  os.path.splitext(curr_subs_dict['filename'])[1]
		download_subtitles([curr_subs])
		subs_out_ENG = subs_out_ENG.replace('.srt',file_type)
		subs_out_ENG = os.path.join(out_directory, subs_out_ENG)
		with open(subs_out_ENG, 'w', encoding='utf-8') as f:
			f.write(curr_subs.text)

		if file_type == '.ass':
			subs_hash.ass_to_srt(subs_out_ENG, subs_out_ENG.replace(file_type,'.srt'))
			subs_out_ENG = subs_out_ENG.replace(file_type,'.srt')
	else:
		subs_out_ENG = None
	return subs_out_ENG, subs_out_FORCED
	"""
	#save_subtitles(video, curr_subs,directory='/home/osmc/.kodi/userdata/addon_data/script.xtreme_vod/temp')

	subtitles = download_best_subtitles([video], languages={Language('eng')}, providers=['opensubtitlescom'],	provider_configs={'opensubtitlescom': opensubtitlescom_credentials, 'opensubtitles': opensubtitles_credentials} , hearing_impaired=False)
	print(subtitles[video])
	save_subtitles(video, subtitles[video],directory='/home/osmc/.kodi/userdata/addon_data/script.xtreme_vod/temp')
	"""
#file_path = "/folder/folder/folder/video_file.mkv"
#subs_out_ENG, subs_out_FORCED = get_subs_file(cache_directory=cache_directory, video_path = file_path, same_folder=False)