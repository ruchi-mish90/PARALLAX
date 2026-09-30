from pathlib import Path
import numpy as np
import cv2

TMC2 = r"C:\Users\graj6\Downloads\P0001\ch2_tmc_ncn_20230605T1503198538_d_img_n18\data\calibrated\20230605\ch2_tmc_ncn_20230605T1503198538_d_img_n18.img"
IIRS = r"C:\Users\graj6\Downloads\P0001\ch2_iir_nci_20221209T1908498944_d_img_n18\data\calibrated\20221209\ch2_iir_nci_20221209T1908498944_d_img_n18.qub"

tmc = np.memmap(TMC2, dtype="<u2", mode="r", shape=(153244,4000))
iirs = np.memmap(IIRS, dtype="<f4", mode="r", shape=(256,10075,250))

# A03 coordinates are LINE,SAMPLE.
iirs_line, iirs_sample = 1800, 0
tmc_line, tmc_sample = 113500, 1200

SX, SY = 9.6805, 8.1776
DX, DY = 3, 18

bands = [160,192,224]

def norm(a):
    a=np.asarray(a,dtype=np.float32)
    a=np.nan_to_num(a,nan=0.0,posinf=0.0,neginf=0.0)

    if a.size == 0:
        raise ValueError("Empty image patch")

    lo,hi=np.percentile(a,[1,99])

    if hi <= lo:
        return np.zeros(a.shape,dtype=np.uint8)

    a=np.clip(a,lo,hi)
    return ((a-lo)/(hi-lo)*255).astype(np.uint8)

print("="*70)
print("PARALLAX A03 INDEPENDENT IMAGE CORRESPONDENCE TEST")
print("="*70)

for band in bands:

    # ---------------------------------------------------------
    # IIRS: [band, LINE, SAMPLE]
    # ---------------------------------------------------------
    iy0=max(0,iirs_line-50)
    iy1=min(iirs.shape[1],iirs_line+51)

    ix0=max(0,iirs_sample-50)
    ix1=min(iirs.shape[2],iirs_sample+51)

    ip=iirs[band,iy0:iy1,ix0:ix1]

    # ---------------------------------------------------------
    # TMC2: [LINE, SAMPLE]
    # ---------------------------------------------------------
    center_line=int(round(tmc_line + DY*SY))
    center_sample=int(round(tmc_sample + DX*SX))

    half_iirs=50
    half_line=int(round(half_iirs*SY))
    half_sample=int(round(half_iirs*SX))

    ty0=max(0,center_line-half_line)
    ty1=min(tmc.shape[0],center_line+half_line+1)

    tx0=max(0,center_sample-half_sample)
    tx1=min(tmc.shape[1],center_sample+half_sample+1)

    tp=tmc[ty0:ty1,tx0:tx1]

    print(f"\nBAND {band}")
    print(f"IIRS patch : {ip.shape}")
    print(f"TMC2 patch : {tp.shape}")

    if ip.size==0 or tp.size==0:
        print("STATUS     : EMPTY PATCH")
        continue

    ip8=norm(ip)
    tp8=norm(tp)

    tp8=cv2.resize(
        tp8,
        (ip8.shape[1],ip8.shape[0]),
        interpolation=cv2.INTER_AREA
    )

    sift=cv2.SIFT_create(
        nfeatures=2000,
        contrastThreshold=0.01,
        edgeThreshold=20
    )

    k1,d1=sift.detectAndCompute(ip8,None)
    k2,d2=sift.detectAndCompute(tp8,None)

    n1=0 if k1 is None else len(k1)
    n2=0 if k2 is None else len(k2)

    print(f"keypoints IIRS : {n1}")
    print(f"keypoints TMC2 : {n2}")

    if d1 is None or d2 is None or len(d1)<2 or len(d2)<2:
        print("good matches   : 0")
        print("RANSAC         : insufficient descriptors")
        continue

    matcher=cv2.BFMatcher(cv2.NORM_L2)
    knn=matcher.knnMatch(d1,d2,k=2)

    good=[]

    for pair in knn:
        if len(pair)==2:
            m,n=pair
            if m.distance < 0.75*n.distance:
                good.append(m)

    print(f"good matches   : {len(good)}")

    if len(good)<4:
        print("RANSAC         : insufficient matches")
        continue

    src=np.float32([k1[m.queryIdx].pt for m in good])
    dst=np.float32([k2[m.trainIdx].pt for m in good])

    M,mask=cv2.estimateAffinePartial2D(
        src,dst,
        method=cv2.RANSAC,
        ransacReprojThreshold=3.0,
        maxIters=3000,
        confidence=0.99
    )

    if M is None or mask is None:
        print("RANSAC         : FAILED")
        continue

    mask=mask.ravel().astype(bool)
    nin=int(mask.sum())

    pred=cv2.transform(
        src.reshape(-1,1,2),M
    ).reshape(-1,2)

    errors=np.linalg.norm(pred-dst,axis=1)

    print(f"RANSAC inliers : {nin}/{len(good)}")
    print(f"inlier ratio   : {nin/len(good):.4f}")

    if nin:
        print(f"median error   : {np.median(errors[mask]):.4f} px")
        print(f"max inlier err : {np.max(errors[mask]):.4f} px")

    print("transform:")
    print(M)

print("\n"+"="*70)
print("A03 INDEPENDENT IMAGE TEST COMPLETE")
print("="*70)

