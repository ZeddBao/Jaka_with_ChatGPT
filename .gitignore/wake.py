import os
from pocketsphinx import LiveSpeech, get_model_path
import pyttsx3


def wake():
    model_path = r"D:\Users\baoze\anaconda3\envs\MechanicalArms\Lib\site-packages\pocketsphinx\model\cmusphinx-zh-cn-5.2"
    x = pyttsx3.init()

    speech = LiveSpeech(
        verbose=False,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False,
        hmm=os.path.join(model_path, 'zh_cn.cd_cont_5000'),
        lm=os.path.join(model_path, '4789.lm'),
        dic=os.path.join(model_path, '4789.dic')
    )
    for phrase in speech:
        print("phrase:", phrase)
        print(phrase.segments(detailed=True))
        # 只要命中上述关键词的内容，都算对
        if str(phrase) in ["形影", "形影 形影", "形影 形影 形影", "啊 形影", "哈哈 形影"]:
            x.say("爷来咯！")
            x.runAndWait()
            return
