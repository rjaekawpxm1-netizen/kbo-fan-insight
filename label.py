import pandas as pd
p="data/raw/youtube/labeled_sample.csv"
df=pd.read_csv(p)
if "label" not in df.columns:
    df["label"]=""
df["label"]=df["label"].astype("object")   # 빈 열이 숫자로 잡혀 문자열 저장 실패하는 것 방지
m={"p":"positive","n":"negative","u":"neutral"}
done=0
for i,row in df.iterrows():
    cur=str(row["label"]).strip()
    if cur and cur!="nan":
        continue
    print(f"\n[{i+1}/{len(df)}] {row['text']}")
    a=input("p=긍정  n=부정  u=중립  (s=건너뜀, q=저장후종료): ").strip().lower()
    if a=="q": break
    if a=="s": continue
    if a in m:
        df.at[i,"label"]=m[a]
        done+=1
        df.to_csv(p,index=False,encoding="utf-8-sig")   # 매번 저장 → 끊겨도 보존
print(f"\n{done}개 라벨링·저장 완료")
