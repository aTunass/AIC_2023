import torch
import InternVideo

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

text_cand = ["an airplane is taking off", "an airplane is flying", "a dog is chasing a ball"]
video = InternVideo.load_video("Team3/video_summary/data/demo.mp4").to(device)

model = InternVideo.load_model("Team3/video_summary/models/InternVideo-MM-B-16.ckpt").to(device)
text = InternVideo.tokenize(text_cand).to(device)

with torch.no_grad():
    text_features = model.encode_text(text)
    video_features = model.encode_video(video.unsqueeze(0))

    video_features = torch.nn.functional.normalize(video_features, dim=1)
    text_features = torch.nn.functional.normalize(text_features, dim=1)
    t = model.logit_scale.exp()
    probs = (video_features @ text_features.T * t).softmax(dim=-1).cpu().numpy()

print("Label probs: ")  # [[9.5619422e-01 4.3805469e-02 2.0393253e-07]]
for t, p in zip(text_cand, probs[0]):
    print("{:30s}: {:.4f}".format(t, p))
