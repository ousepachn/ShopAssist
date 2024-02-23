import instaloader
import pandas as pd
import glob

posts_data = []

usernames=["whatsmitafound"]  ## (hydrationceo, whatsmitafound, mkbhd)
u=usernames[0]
ig=instaloader.Instaloader()
pf=instaloader.Profile

# Load a profile from an Instagram handle
profile = pf.from_username(ig.context, u)
print(profile.username)
print('username:',profile.username)
print('followers:',profile.followers)
print('posts:',profile.mediacount)
print('bio:', profile.biography)
print('links:', profile.external_url) 
pic=ig.download_profiles([profile],posts=False)
posts = profile.get_posts()


for i, p in enumerate(posts):
    if i >= 50:
        break
    
    posts_path = f'posts'
    ig.download_post(p, f'{posts_path}')
    
    jpg_files = glob.glob(f'posts/*{str(p.date_utc)[:10]}_{str(p.date_utc)[11:12]}*.jpg')
    vid_files = glob.glob(f'posts/*{str(p.date_utc)[:10]}_{str(p.date_utc)[11:12]}*.mp4')

    if jpg_files:
        thumbnail_url=jpg_files[0]
    else:
        thumbnail_url=None

    if p.is_video:
        url=vid_files[0]
    else:
        url=jpg_files[0]

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

df = pd.DataFrame(posts_data)

df.to_pickle(f'all-posts.pkl')
df.to_csv(f'all-posts.csv', index=False)


# df.to_pickle(f'hydrationceo-posts.pkl')
# df.to_csv(f'hydrationceo-posts.csv', index=False)

   

