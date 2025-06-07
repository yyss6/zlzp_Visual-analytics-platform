import jieba
from matplotlib import pylab as plt
from wordcloud import WordCloud
from PIL import Image
import numpy as np
import json
from myApp.models import JobInfo
import os

# 修改get_img函数，使其接受数据作为参数
def get_img(data_list, targetImageSrc, resImageSrc):
    text = ''
    for item in data_list:
        # Assuming each item in data_list is a string to process
        if item and isinstance(item, str) and item.strip() != '无' and item.strip() != "":
             try:
                 # Try to load as JSON and process if it's a list of strings
                 tags_list = json.loads(item)
                 if isinstance(tags_list, list) and len(tags_list) > 0 and isinstance(tags_list[0], str) and tags_list[0].strip() != "":
                      # Assuming companyTags format like ["tag1,tag2", ...]
                     for tags_str in tags_list:
                          if isinstance(tags_str, str):
                             companyTagsArr = tags_str.split('，')
                             for tag in companyTagsArr:
                                  text += tag
                 else:
                     # If not a list or empty list, treat as raw string if it is one
                     if isinstance(item, str):
                         text += item

             except (json.JSONDecodeError, TypeError):
                 # If JSON parsing fails, treat as raw string if it is one
                  if isinstance(item, str):
                     text += item


    # 处理分词和停用词（如果需要）
    data_cut = jieba.cut(text, cut_all=False)
    string = ' '.join(data_cut)

    # 图片
    # Ensure the target image file exists
    if not os.path.exists(targetImageSrc):
        print(f"Error: Target image file not found at {targetImageSrc}")
        return False # Indicate failure

    img = Image.open(targetImageSrc)
    img_arr = np.array(img)
    wc = WordCloud(
        background_color='white',
        mask=img_arr,
        font_path='STHUPO.TTF' # Make sure this font file exists and is accessible
    )
    wc.generate_from_text(string)

    # 绘制图片
    fig = plt.figure(1)
    plt.imshow(wc)
    plt.axis('off')

    # Ensure the output directory exists
    output_dir = os.path.dirname(resImageSrc)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.savefig(resImageSrc, dpi=800)
    plt.close(fig) # Close the figure to free memory
    return True # Indicate success



# get_img('companyTags','../static/1.png','../static/companyTags_cloud.png')
