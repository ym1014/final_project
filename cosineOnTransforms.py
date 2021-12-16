# run centos in docker
# yum install python38
# pip3 install torch torchvision torchaudio
# pip3 install transformers[torch]
# python3 -c "from transformers import pipeline; print(pipeline('sentiment-analysis')('we love you'))"
# python3 cosineOnTransforms.py

import math
from transformers import AutoTokenizer


def getIdsWithCls(stra, strb):
	tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
	encoded_input = tokenizer([stra,strb])	
	print (encoded_input)

	return encoded_input['input_ids']
		

def cosineSimilarity(sa, sb):	

	docw = set(sa) | set(sb)

	wfa = []
	wfb = []
	for k in docw:
		wfa.append(sa.count(k))
		wfb.append(sb.count(k))

	dotp = 0
	dota = 0
	dotb = 0 
	for i in range(len(wfa)):
		dotp += wfa[i]*wfb[i]
		dota += wfa[i]*wfa[i]
		dotb += wfb[i]*wfb[i]

	ans = dotp / (math.sqrt(dota)+math.sqrt(dotb))

	return  ans

def calCsForStr(stra, strb):
	sa,sb = getIdsWithCls(stra, strb)
	ans = cosineSimilarity(sa, sb)
	return ans

if __name__ == "__main__":
	ans = calCsForStr('a b c d', 'b c d e f g')
	print (ans)


	ans = calCsForStr('She is a woman', 'I an a man')
	print (ans)