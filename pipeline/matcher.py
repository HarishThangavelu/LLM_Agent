from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def match_jobs(resume_text, jobs):

    corpus = [resume_text] + [job["title"] for job in jobs]

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(corpus)

    resume_vector = vectors[0]
    job_vectors = vectors[1:]

    scores = cosine_similarity(resume_vector, job_vectors)[0]

    for i, job in enumerate(jobs):
        job["score"] = float(scores[i])

    jobs = sorted(jobs, key=lambda x: x["score"], reverse=True)

    return jobs