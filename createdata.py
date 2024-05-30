import instaloader
import pandas as pd
import glob
import os
import pandas as pd
import requests
import time


def getprofiledata(username):
    profile = pf.from_username(ig.context, username)
    profile_data = {
        "creatorid":  profile.username,
        "followers": profile.followers,
        "followees": profile.followees,
        "posts": profile.mediacount,
        "bio": profile.biography,
        "links": profile.external_url,
        "name": profile.full_name,
        "date_refreshed": pd.to_datetime('today'), 
        }
    ig.download_profilepic(profile) # Fix the typo in the function call
    jpg_files = glob.glob(f'posts/{profile.username}/*profile_pic.jpg')
    if jpg_files:
        latest_profile_pic = max(jpg_files, key=os.path.getctime)
        profile_data['profile_pic'] = latest_profile_pic
    else:
        profile_data['profile_pic'] = None
    print(profile.username)
    print('username:',profile.username)
    print('followers:',profile.followers)
    print('posts:',profile.mediacount)
    print('bio:', profile.biography)
    print('links:', profile.external_url) 

    return profile_data

def getpostsdata(profile):
    posts = profile.get_posts()
    posts_data = []
    error_list = []
    for i, p in enumerate(posts):
        if i > 70:
            break
        folder_name=os.path.join('posts', profile.username )
        #Create folder for creator, if none exists
        if not os.path.exists(folder_name):
                os.makedirs(folder_name)
        try:
            ig.download_post(p, folder_name)
        except Exception as e:
            error_data = {
                "influencer_id": profile.username,
                "post_id": p.shortcode,
                "error_code": str(e)
            }
            error_list.append(error_data)
            print(f"Error downloading post {p.shortcode}: {str(e)}")
        else:
            jpg_files = glob.glob(f'posts/{influencer}/*{str(p.date_utc)[:10]}_{str(p.date_utc)[11:13]}-{str(p.date_utc)[14:16]}*.jpg')
            vid_files = glob.glob(f'posts/{influencer}/*{str(p.date_utc)[:10]}_{str(p.date_utc)[11:13]}-{str(p.date_utc)[14:16]}*.mp4')
            print(f'posts/{influencer}/*{str(p.date_utc)[:10]}_{str(p.date_utc)[11:13]}-{str(p.date_utc)[14:16]}*.jpg')

            if jpg_files:
                thumbnail_url=jpg_files[0]
            else:
                thumbnail_url=None

            if p.is_video:
                url=vid_files[0]
            else:
                url=jpg_files[0]
            print('reading post:', i,p.shortcode)
            post_data = {
                "creatorid":  profile.username,
                "post_id": p.shortcode,
                "title": p.title,
                "caption": p.caption,
                "likes": p.likes,
                "thumbnail_url": thumbnail_url,
                "url": url,
                "date_utc": p.date_utc,
                "typename": p.typename,
                "caption_hashtags": p.caption_hashtags,
                "is_video": p.is_video
            }
            posts_data.append(post_data)
    return posts_data,error_list




ig=instaloader.Instaloader(dirname_pattern="posts\\{profile}",save_metadata=False,compress_json=False)
pf=instaloader.Profile  

sa_posts_data = []
sa_profiles_data = [] 
sa_errors=[]
influencer_list=[#'kirtitewani','hemali.mistry',
                 #'thescenenewyork','payalforstyle',
                 #'fatimaa.younus',
                 'reeti_shop','hydrationceo', 'whatsmitafound','justanotherhappygirl','radhidevlukia']
influencer_list_test=['hemali.mistry','radhidevlukia']


for influencer in influencer_list:
# ['hydrationceo', 'whatsmitafound', 'mkbhd']:
    
    print('S1 reading influencer:', influencer)
    profile = pf.from_username(ig.context, influencer)
    profile_data=getprofiledata(influencer)
    sa_profiles_data.append(profile_data)
    print('S2 updated profile data:', influencer)
    print('S3 reading posts data:', influencer)
    posts_data,Error_list=getpostsdata(pf.from_username(ig.context, influencer))
    sa_posts_data.append(posts_data)
    sa_errors.append(Error_list)
    print('All posts read from influener, Waiting for 300 seconds too cool system...')
    for remaining in range(300, 0, -1):
        print(f"Sleeping for {remaining} seconds...", end='\r')
        time.sleep(1)
    print("Sleeping complete!")

combined_posts_data = []
for sublist in sa_posts_data:
    combined_posts_data.extend(sublist)

combined_errors_data = []
for sublist in sa_errors:
    combined_errors_data.extend(sublist)

df_combined_posts = pd.DataFrame(combined_posts_data)
df_profiles = pd.DataFrame(sa_profiles_data)
df_errors = pd.DataFrame(combined_errors_data)

df_combined_posts.to_pickle(f'all-posts-05272024v2.pkl')
df_profiles.to_pickle(f'all-profiles05272024v2.pkl')
df_errors.to_pickle(f'all-errors05272024v2.pkl')

df_combined_posts.to_csv(f'all-posts-05272024.csv', index=False)

unique_influencers = list(set([post[0]['creatorid'] for post in sa_posts_data]))