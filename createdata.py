import instaloader
import pandas as pd
import glob
import os
import pandas as pd
import requests


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
    for i, p in enumerate(posts):
        if i >= 50:
            break
        folder_name=os.path.join('posts', profile.username )
        #Create folder for creator, if none exists
        if not os.path.exists(folder_name):
                os.makedirs(folder_name)
        ig.download_post(p, folder_name)
        
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
    return posts_data




ig=instaloader.Instaloader(dirname_pattern="posts\\{profile}",save_metadata=False,compress_json=False)
pf=instaloader.Profile  

sa_posts_data = []
sa_profiles_data = [] 

for influencer in ['hydrationceo', 'whatsmitafound', 'mkbhd']:
     print('S1 reading influencer:', influencer)
     profile = pf.from_username(ig.context, influencer)
     profile_data=getprofiledata(influencer)
     sa_profiles_data.append(profile_data)
     print('S2 updated profile data:', influencer)
     print('S3 reading posts data:', influencer)
     posts_data=getpostsdata(pf.from_username(ig.context, influencer))
     sa_posts_data.append(posts_data)

combined_posts_data = []
for sublist in sa_posts_data:
    combined_posts_data.extend(sublist)

df_combined_posts = pd.DataFrame(combined_posts_data)
df_profiles = pd.DataFrame(sa_profiles_data)

df_combined_posts.to_pickle(f'all-posts-0302024.pkl')
df_profiles.to_pickle(f'all-profiles03052024.pkl')

df_combined_posts.to_csv(f'all-posts.csv', index=False)

