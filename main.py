"""Social listening, audience segmentation and randomized campaign analysis."""
import argparse,csv,re,sqlite3,math
from pathlib import Path
from collections import Counter
import numpy as np
from common import save_report,table

POS={'love','great','helpful','excellent','amazing'}; NEG={'bad','slow','confusing','hate','broken'}
def sentiment(text):
    tokens=re.findall(r'\w+',text.lower()); score=0
    for i,t in enumerate(tokens):
        val=int(t in POS)-int(t in NEG)
        if i and tokens[i-1] in {'not','never'}: val=-val
        score+=val
    return 'positive' if score>0 else 'negative' if score<0 else 'neutral'

def entities(text):
    # Transparent gazetteer NER baseline; intentionally limited to known entities.
    return [e for e in ['Acme','Mumbai','Delhi','StreamPlus'] if re.search(r'\b'+re.escape(e)+r'\b',text,re.I)]

def theme(text):
    tokens=set(re.findall(r'\w+',text.lower()))
    themes={'pricing':{'price','cost','expensive'},'quality':{'audio','video','broken'},'discovery':{'recommendations','discover','search'}}
    scores={k:len(tokens&v) for k,v in themes.items()}; best=max(scores,key=scores.get)
    return best if scores[best] else 'other'

def kmeans(x,k=3):
    scaled=(x-x.mean(axis=0))/np.maximum(x.std(axis=0),1e-9); centers=scaled[np.random.default_rng(8).choice(len(x),k,replace=False)]
    for _ in range(60):
        labels=((scaled[:,None]-centers)**2).sum(axis=2).argmin(axis=1)
        new=np.array([scaled[labels==j].mean(axis=0) if np.any(labels==j) else centers[j] for j in range(k)])
        if np.allclose(new,centers): break
        centers=new
    return labels

def experiment(a,b):
    if min(len(a),len(b))<2: raise ValueError('Each arm needs at least two users')
    delta=float(np.mean(b)-np.mean(a)); se=math.sqrt(float(np.var(a,ddof=1)/len(a)+np.var(b,ddof=1)/len(b)))
    p=math.erfc(abs(delta)/max(se,1e-12)/math.sqrt(2))
    return delta,(delta-1.96*se,delta+1.96*se),p

def run(out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(13)
    fixtures=[('I love Acme recommendations in Mumbai','positive','discovery'),('StreamPlus audio is broken in Delhi','negative','quality'),('Acme price is not great','negative','pricing'),('The video is helpful','positive','quality'),('Search on StreamPlus','neutral','discovery'),('I never hate the audio','positive','quality'),('The cost is confusing','negative','pricing'),('Acme update today','neutral','other'),('Amazing video in Delhi','positive','quality')]
    posts=[]
    for i in range(450):
        text,label,topic=fixtures[i%len(fixtures)]; posts.append((i,['Instagram','Facebook','Twitter'][i%3],text,label,topic))
    with (out/'posts.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['post_id','platform','text','fixture_sentiment','fixture_theme']); w.writerows(posts)
    db=sqlite3.connect(out/'social.sqlite'); db.execute('DROP TABLE IF EXISTS posts'); db.execute('CREATE TABLE posts(id INT, platform TEXT, text TEXT, sentiment TEXT, theme TEXT)'); db.executemany('INSERT INTO posts VALUES (?,?,?,?,?)',[(i,p,t,sentiment(t),theme(t)) for i,p,t,_,_ in posts]); db.commit()
    breakdown=db.execute('SELECT platform,sentiment,COUNT(*) FROM posts GROUP BY platform,sentiment').fetchall(); db.close()
    # Separate hand-labelled challenge cases, not the templates used to create posts.
    challenge=[('The recommendations are excellent','positive'),('not helpful search','negative'),('I love the video but hate the price','neutral'),('Audio update released','neutral'),('great, another broken video','negative'),('This is sick','positive')]
    correct=sum(sentiment(t)==l for t,l in challenge)
    users=np.vstack([rng.normal([5,3,2],[1,.6,.5],(100,3)),rng.normal([20,12,3],[2,2,.6],(100,3)),rng.normal([9,4,15],[1.5,1,2],(100,3))]); labels=kmeans(users)
    summaries=[(j,int(sum(labels==j)),*np.round(users[labels==j].mean(axis=0),1)) for j in range(3)]
    # Independent users assigned before outcomes; one binary conversion per user.
    a=rng.binomial(1,.10,2500); b=rng.binomial(1,.125,2500); delta,ci,p=experiment(a,b)
    with (out/'experiment.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['user_id','arm','converted']); w.writerows((i,'control',int(v)) for i,v in enumerate(a)); w.writerows((i+len(a),'treatment',int(v)) for i,v in enumerate(b))
    metrics={'Challenge sentiment accuracy':f'{correct}/{len(challenge)}','Conversion difference pp':round(delta*100,2),'95% CI pp':f'[{ci[0]*100:.2f}, {ci[1]*100:.2f}]','Two-sided p value':round(p,4),'Simulated users':len(a)+len(b)}
    save_report(out,'Social Campaign Lab',metrics,[('Platform sentiment (SQL)',table(['platform','sentiment','posts'],breakdown)),('Unseen challenge cases',table(['text','expected','predicted'],[(t,l,sentiment(t)) for t,l in challenge])),('Audience segments',table(['cluster','users','sessions','watch minutes','shares'],summaries)),('Entity and theme extraction',table(['text','entities','theme'],[(t,', '.join(entities(t)),theme(t)) for t,_,_ in fixtures[:5]])),('Experiment interpretation','<p>Randomized synthetic demonstration: absolute difference in conversion rates with a normal-approximation interval and unpooled Wald test. No real lift claim. A real experiment needs prespecified sample size, assignment checks, guardrails and no repeated peeking. Sentiment is a lexicon baseline; sarcasm, slang and mixed sentiment remain failure modes. Clusters are descriptive, not causal.</p>')]); return metrics

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',default='results'); print(run(p.parse_args().out))
