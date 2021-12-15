import os
import time
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-arm64"
import pyterrier as pt
# from pyterrier.measures import *
import pandas as pd 
import spacy

nlp = spacy.load('en_core_web_sm')

def initPt(termpipelines):
	if not pt.started():
		pt.init(version='5.6')
		print ('pt is  started already.')

	pt.set_property("termpipelines",termpipelines)

def generateData():
	fnames = os.listdir('./wiki')
	# print (fnames)
	title = ''
	text = ''
	for fname in fnames:
		with open('./wiki/'+fname, 'r') as f:
			for line in f:
				if line.startswith('[[') and line.strip().endswith(']]'):
					if len(title) > 0:
						if len(text) <= 0:
							print('Error text is empty', title, fname)
						yield {'docno':title,'text':text}
						# break
					title = line.split('[[')[1].split(']]')[0]
					text = ''
				else:
					text += line

		print ('file done', fname)

	if len(title) > 0:
		yield {'docno':title,'text':text}

def generateIndex(termpipelines):
	indexbasic = 'wikinormal' if termpipelines == '' else 'wikistem'

	if os.path.isfile('./'+indexbasic+'/data.properties'):
		indexref = pt.IndexRef.of('./'+indexbasic+'/data.properties')
		
	else:
		iter_indexer = pt.IterDictIndexer('./'+indexbasic)
		indexref = iter_indexer.index(generateData(), meta=['docno', 'text'])

	index = pt.IndexFactory.of(indexref)

	return index


def createQuery(termpipelines):
	onequestion = []
	questions = []
	with open('questions.txt','r') as f:
		for line in f:
			# print (line)
			kline = line.replace('\n','')
			if len(kline) > 0:
				qs = kline
				if len(onequestion) == 1:	
					kline = kline + ' ' + onequestion[0]					
					doc = nlp(kline.replace("'",' '))
					if termpipelines == '':
						qs = ' '.join([t.text for t in doc if not t.is_punct ])
					else:
						qs = ' '.join([t.lemma_ for t in doc if not t.is_punct ])

				
				onequestion.append(qs)		
			else:
				questions.append(onequestion)
				onequestion = []

	qdf = pd.DataFrame(questions, columns=['category','query','ans'])
	qdf = qdf.reset_index()
	qdf['index'] = qdf['index'].astype(str)
	qdf.columns = ['qid','category','query','ans']

	return qdf

def experimentdata(index, qdf):
	topics = qdf[['qid','query']]
	qrels = qdf[['qid','ans']]
	qrels.columns=['qid','docno']
	qrels['label'] = '1'

	bm25 = pt.BatchRetrieve(index, wmodel='BM25')
	tdidf = pt.BatchRetrieve(index, wmodel='TF_IDF')
	dph = pt.BatchRetrieve(index, wmodel='DPH')
	# dlh = pt.BatchRetrieve(index, wmodel='DLH')
	# dlm = pt.BatchRetrieve(index, wmodel='Dirichlet_LM')

	tdbm =  tdidf +  dph

	return pt.Experiment([tdbm, dph, bm25, tdidf], topics, qrels, eval_metrics=['map','P_5','ndcg','recip_rank'])

	# return pt.Experiment([bm25, tdidf, dph, dlh], topics, qrels, eval_metrics=['map','P_5','ndcg','recip_rank'])

def transformQuery(index, wmodel, resnum, qdf, resname):
	topics = qdf[['qid','query']]

	br = pt.BatchRetrieve(index, wmodel=wmodel,num_results=resnum)

	res = br.transform(topics)

	# print (res)

	diffdf = pd.merge(res, qdf, on=['qid'], how='left')

	diffdf['result'] = diffdf['docno'] == diffdf['ans']

	diffdf.to_csv(resname)

	return diffdf.groupby('result').size().reset_index()

def transforMultiQuery(index, wm1,wm2, qdf,resname):
	topics = qdf[['qid','query']]

	br1 = pt.BatchRetrieve(index, wmodel=wm1,num_results=10)
	br2 = pt.BatchRetrieve(index, wmodel=wm2,num_results=10)

	res = (br1+br2).transform(topics)

	res = res.drop_duplicates(subset=['qid'], keep='first')

	diffdf = pd.merge(res, qdf, on=['qid'], how='left')

	diffdf['result'] = diffdf['docno'] == diffdf['ans']

	diffdf.to_csv(resname)

	return diffdf.groupby('result').size().reset_index()

if __name__ == "__main__":

	start = time.time()

	# termpipelines = ''
	termpipelines = 'Stopwords,PorterStemmer'
	
	initPt(termpipelines)	
	end = time.time()
	print ('initPt done cost:', end-start)
	start = end

	index = generateIndex(termpipelines)
	end = time.time()
	print ('generateIndex done cost:', end-start)
	start = end

	qdf = createQuery(termpipelines)
	end = time.time()
	print ('createQuery done cost:', end-start)
	start = end

	res = experimentdata(index, qdf)
	print ('experiment:')
	print (res)
	end = time.time()
	print ('experiment done cost:', end-start)
	start = end

	res = transformQuery(index, "BM25", 1, qdf, 'BM25normal-1.csv')
	print ('res with BM25-1:')
	print (res)
	end = time.time()
	print ('createQuery with BM25 done cost:', end-start)
	start = end


	res = transformQuery(index, "TF_IDF", 1, qdf, 'TF_IDFnormal-1.csv')
	print ('res with TF_IDF-1:')
	print (res)
	end = time.time()
	print ('createQuery with TF_IDF done cost:', end-start)
	start = end


	res = transformQuery(index, "DPH", 1, qdf, 'DPH.csv')
	print ('res with DPH-1:')
	print (res)
	end = time.time()
	print ('createQuery with DPH done cost:', end-start)
	start = end

	res = transforMultiQuery(index, "TF_IDF", "DPH",  qdf, 'tfdph.csv')
	print ('res with tfdph-1:')
	print (res)
	end = time.time()
	print ('createQuery with tfdph done cost:', end-start)
	start = end