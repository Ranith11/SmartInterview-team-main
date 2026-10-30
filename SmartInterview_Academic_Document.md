# SmartInterview: An Adaptive AI-Powered Mock Interview and Skill Evaluation Platform Using Retrieval-Augmented Generation and Bloom's Taxonomy

---

## 1. INTRODUCTION

Getting a job in today's market is harder than it used to be. Students graduating from colleges, especially in technical fields like computer science and engineering, face intense competition. One of the biggest hurdles they encounter is the technical interview. Performing well in a technical interview requires not just theoretical knowledge, but also the ability to communicate clearly, think on the spot, and adapt to unexpected questions.

Unfortunately, most students do not get enough practice before they sit for real interviews. The traditional ways of preparing — reading textbooks, watching videos, or asking a friend to ask some questions — are limited. They do not replicate the pressure and structure of a real interview. Textbooks test knowledge but not communication. Friends may not ask the right questions. Online coding platforms test programming skills but ignore verbal and conceptual questioning entirely.

At the same time, companies receive hundreds or even thousands of applications for a single job opening. Screening resumes manually is slow and prone to human error. Many qualified candidates are rejected simply because their resumes use different words to describe the same skills that the recruiter is looking for. The first round of technical interviews is often repetitive and time-consuming for interviewers, and scheduling these interviews adds further delays.

This situation creates a clear need on both sides. Candidates need a realistic, structured, and personalised way to practise for interviews. Recruiters and organisations need efficient, fair, and scalable tools to evaluate candidates. Artificial intelligence, particularly large language models and speech-recognition technology, now makes it possible to address both these needs. AI can generate relevant interview questions, listen to spoken answers, evaluate responses, and provide structured feedback — all without requiring a human interviewer to be present.

Our project, **SmartInterview**, is built to address this need. It is an AI-powered mock interview platform that adapts to each candidate based on their resume, the job they are targeting, and how well they answer during the session. It uses established educational principles (Bloom's Taxonomy) to progressively adjust question difficulty, and it draws from a curated technical knowledge base to ensure questions are grounded in real concepts rather than randomly generated.

---

## 2. PROBLEM STATEMENT

### What problem currently exists?

Students and job seekers preparing for technical interviews lack access to a realistic, structured, and personalised practice environment. Most available options are either too generic (random question banks), too narrow (coding-only platforms), or too dependent on human availability (peer mock interviews).

### Who faces this problem?

- **Students** preparing for campus placements and off-campus interviews.
- **Fresh graduates** entering the job market for the first time.
- **Working professionals** switching roles or domains.
- **Training institutes and colleges** that want to help their students prepare systematically.
- **Recruiters and companies** that spend excessive time conducting repetitive first-round interviews.

### Why is the problem difficult?

- Real interviews are unpredictable — questions change based on the candidate's previous answers.
- Evaluating an interview requires judging not just technical correctness, but also communication quality, depth of understanding, and problem-solving approach.
- Personalising questions to match a specific candidate's resume and target job is complex.
- Providing consistent, unbiased feedback at scale is difficult with human interviewers.
- Existing automated tools either focus only on coding challenges or use rigid, non-adaptive question sets.

### What limitations exist in current approaches?

| Current Approach | Limitation |
|---|---|
| Textbooks and notes | No interactivity, no feedback, no question adaptation |
| Online coding platforms (e.g., LeetCode, HackerRank) | Focus on code only; ignore verbal communication and conceptual depth |
| Peer mock interviews | Depend on human availability; inconsistent quality and feedback |
| Enterprise platforms (e.g., HireVue, Talview) | Designed for employers, not learners; not freely accessible |
| General AI chatbots | Not structured for interview simulation; no built-in evaluation rubric |

### What gap does the proposed application try to address?

The proposed application tries to fill the gap between generic AI conversation and a **structured, domain-specific, resume-aware, adaptive interview experience** with built-in evaluation and feedback — something that no single existing tool currently provides as an integrated package for individual learners.

---

## 3. BASE PAPER

This project is supported by two published research papers that explore AI-driven interview and recruitment systems.

### Base Paper 1

**Title:** "AI Mock Interview: An Intelligent Voice-Driven Interview Simulation System using Gemini AI and Whisper"

**Authors:** Abdul Wahid, Aditya Jha, Meerhan Munshi, Sumit Sonwane, Prof. Amit Chakrawarti

**Published in:** International Journal of Engineering Research & Technology (IJERT), Vol. 15, Issue 03, March 2026. ISSN: 2278-0181.

**Main Objective:**
The paper presents the design of an AI-based mock interview system that uses voice interaction to simulate a realistic technical interview experience for students and job seekers.

**Problem Addressed:**
The paper identifies that existing interview preparation tools are fragmented. Coding platforms like LeetCode and HackerRank test only programming skills and ignore verbal communication. Peer-to-peer platforms like Pramp depend on human availability and provide no automated evaluation. Enterprise platforms like HireVue are built for employers, not learners. No single platform combines voice interaction, resume-aware questions, automated evaluation, and structured reporting.

**Main Idea and Approach:**
The system allows a candidate to upload their resume and select a technical domain. Using Google Gemini (a large language model), the system generates interview questions personalised to the candidate's resume and experience. The candidate answers by speaking, and their voice is converted to text using OpenAI's Whisper model. Based on the conversation, the system evaluates the candidate's performance across multiple dimensions — technical depth, communication skills, problem-solving ability — and generates a downloadable PDF report.

**Important Findings:**
- The paper found that a single integrated platform combining voice interaction, resume parsing, adaptive questioning, AI-based evaluation, and PDF reporting fills a significant gap in the existing landscape.
- The system supports six technical domains and is designed for iterative self-improvement.
- The paper identifies future work areas including emotion analysis, adaptive difficulty using reinforcement learning, behavioural interview support, and video-based non-verbal assessment.

**Relevance to Our Project:**
This paper directly validates the concept of our SmartInterview application. Both systems aim to provide a personalised, AI-driven, voice-enabled interview preparation platform. Our project extends several ideas from this paper — particularly adaptive difficulty adjustment (using Bloom's Taxonomy) and grounding questions in a structured knowledge base (using RAG and ChromaDB).

---

### Base Paper 2

**Title:** "Autonomous AI Interview Engine"

**Authors:** MK Nagarajan, Avinash Kumar, Itha Venkata Sai Vignesh, Altamas Nehal, Mohamad Musthafa

**Published in:** Indian Journal of Modern Research and Reviews, Volume 4, Issue 2, February 2026. (Peer-Reviewed Journal)

**Main Objective:**
The paper proposes an autonomous AI system that automates both resume screening and technical interviewing as a unified recruitment pipeline.

**Problem Addressed:**
The paper highlights that traditional Applicant Tracking Systems (ATS) use keyword-based matching (like TF-IDF), which often rejects qualified candidates simply because they use different words to describe the same skills. Additionally, first-round technical interviews are repetitive, time-consuming, and subject to interviewer bias. Text-based chatbot interview systems lack natural voice interaction and cannot adapt questions dynamically.

**Main Idea and Approach:**
The system uses Sentence-BERT (S-BERT) to perform semantic similarity matching between candidate resumes and job descriptions. Instead of matching keywords, it understands the meaning of phrases, leading to fairer candidate ranking. For the interview phase, the system uses large language models to conduct voice-based, adaptive interviews where question difficulty adjusts based on the candidate's responses. The system generates structured evaluation reports with both quantitative scores and qualitative feedback.

**Important Findings:**
- Semantic similarity (meaning-based matching) significantly outperforms keyword-based matching for resume screening.
- The proposed system is expected to reduce initial screening time by approximately 70–80%.
- Autonomous interviews ensure consistent evaluation standards and reduce human bias.
- Structured evaluation reports improve transparency in the hiring process.

**Relevance to Our Project:**
This paper reinforces the importance of semantic understanding in both resume analysis and interview evaluation. Our SmartInterview platform similarly uses semantic embeddings (all-MiniLM-L6-v2) and skill mapping between resumes and job descriptions. The paper's emphasis on adaptive questioning and structured evaluation aligns closely with our project's approach.

---

## 4. RESEARCH GAP

After reviewing the two base papers and the broader landscape of interview preparation tools, the following gaps can be identified:

### Gap 1: Lack of Structured Difficulty Progression

Both base papers describe adaptive questioning — where the system changes questions based on responses. However, neither paper uses a **formal educational framework** to guide this adaptation. Questions may become harder or easier, but there is no defined structure (such as moving from "remembering" to "analysing" to "creating") that ensures a comprehensive assessment of cognitive ability. Our project addresses this by incorporating **Bloom's Taxonomy**, a well-established educational model, to systematically progress through six levels of cognitive complexity.

### Gap 2: No Grounding of Questions in a Verified Knowledge Base

The systems described in both papers generate questions purely from the language model's training data. While powerful, this approach can occasionally produce questions that are vague, outdated, or not grounded in verified technical concepts. Our project addresses this by using **Retrieval-Augmented Generation (RAG)** with a ChromaDB vector knowledge base, ensuring that generated questions are anchored in real, curated technical material.

### Gap 3: Limited Multi-Signal Evaluation

Both papers describe evaluation based on the language model's overall judgement. Our project uses a **multi-signal evaluation approach** with five distinct metrics (technical accuracy, completeness, relevance, semantic similarity, and concept coverage), making the assessment more transparent and granular.

### Gap 4: No Academic/Syllabus Mode

Both papers focus exclusively on job interviews. There is no provision for students who want to practise based on their **course syllabus or study material** rather than a job description. Our project includes a Syllabus Mode that allows students to upload course material and get interviewed on that content.

### Gap 5: No Long-Term Performance Tracking

The systems in both papers are designed for single-session use. They do not track a candidate's performance over multiple sessions to show improvement trends. Our project includes a **performance analytics dashboard** that tracks historical performance across sessions.

> **Note:** These gaps are identified at the application and practical level. We are not claiming that the research in the base papers is flawed or incomplete. Rather, we are identifying practical opportunities where our application extends their work.

---

## 5. PROPOSED SOLUTION

### What the Application Does

SmartInterview is a mock interview platform where a user can upload their resume and a job description (or course material), and the system conducts a structured, voice-enabled interview session. The system asks questions that are personalised to the user's profile, adapts the difficulty based on how well the user answers, and provides a detailed performance evaluation at the end.

### What Problem It Attempts to Solve

It provides students and job seekers with a **realistic, repeatable, and structured** interview practice environment that closely mimics the dynamics of a real technical interview — something that static question banks, random practice, or casual conversations with friends cannot achieve.

### Who Can Use It

- College students preparing for campus placements.
- Graduates preparing for job interviews.
- Students wanting to test themselves on their course syllabus.
- Training centres and colleges looking for a structured preparation tool.
- Professionals practising for role changes or promotions.

### How It Is Different from General-Purpose Tools

Unlike a general AI chatbot (where the user must know what to ask and how to structure the conversation), SmartInterview:

- **Analyses the user's resume and target job** to automatically determine which topics and skills to focus on.
- **Follows a defined interview workflow** — from skill mapping to adaptive questioning to evaluation to report generation.
- **Adjusts difficulty systematically** using Bloom's Taxonomy levels, not random variation.
- **Grounds questions in verified technical content** through a vector knowledge base.
- **Evaluates performance using multiple specific metrics**, not just a general impression.
- **Produces a downloadable PDF report** with structured scores and recommendations.
- **Tracks performance across sessions** so the user can see improvement over time.

### What Value It Provides

- Saves time spent searching for interview questions.
- Provides a consistent and structured practice experience.
- Gives measurable, multi-dimensional feedback.
- Allows unlimited practice sessions at the user's convenience.
- Helps users identify specific strengths and weaknesses.

---

## 6. WHY DO WE NEED THIS APPLICATION WHEN CHATGPT ALREADY EXISTS?

This is a fair and important question. ChatGPT (and similar general-purpose AI assistants) is a powerful tool that can already do many things related to interview preparation. A user can ask ChatGPT to conduct a mock interview, generate questions, or evaluate answers. We do not claim that ChatGPT cannot do these things.

However, there are meaningful differences between using a general-purpose AI assistant and using a **purpose-built, structured interview platform**. Let us examine them honestly.

### What ChatGPT Can Do

- Generate interview questions on almost any topic.
- Evaluate answers if asked to.
- Simulate a mock interview conversation.
- Provide tips and suggestions for interview preparation.

### What ChatGPT Does Not Do (By Default)

- It does not automatically read and analyse a user's resume and a target job description to determine which skills to focus on.
- It does not follow a systematic difficulty progression based on an educational framework.
- It does not retrieve questions from a curated, domain-specific knowledge base.
- It does not track performance across multiple sessions.
- It does not use multiple distinct evaluation metrics (it gives a general assessment).
- It does not generate structured, downloadable PDF reports.
- It does not provide a voice-based interview interface with speech-to-text and text-to-speech built in.
- It does not have a "Syllabus Mode" for academic study sessions.

### The Core Difference

ChatGPT is a **general-purpose conversation tool**. It can do many things, but the user must know what to ask and how to structure the session. The quality and consistency of the experience depend heavily on how well the user prompts it.

SmartInterview is a **purpose-built application** with a defined workflow. The user uploads their resume and job description, and the system handles everything else — skill mapping, question generation, difficulty adaptation, evaluation, and reporting — without requiring the user to craft prompts or manage the conversation.

### An Analogy

Consider this: Google Sheets and a dedicated accounting software (like Tally) can both handle financial data. Google Sheets is more flexible and can do almost anything if you know how to set it up. But a business owner who needs to generate invoices, track expenses, and file tax reports will benefit from Tally because it provides a structured, purpose-built workflow that handles these tasks consistently without requiring manual setup every time.

Similarly, SmartInterview provides a structured, consistent, and specialised interview preparation workflow that a general AI assistant does not provide out of the box.

### A Balanced Answer

We acknowledge that a technically skilled user who knows how to prompt ChatGPT effectively can achieve many of the same outcomes. Our application is not intended to replace ChatGPT. It is intended to serve users who:

- Want a ready-made, structured interview experience without manual prompt engineering.
- Need consistent, trackable evaluation across sessions.
- Prefer a dedicated platform with resume analysis, voice interaction, and reporting built in.
- Benefit from systematic difficulty progression rather than ad-hoc conversation.

The actual reason for developing this application is not that ChatGPT is incapable — it is that a **structured, specialised tool reduces the effort and inconsistency** involved in using a general-purpose tool for a specific task.

---

## 7. WHY WOULD A USER USE OUR APPLICATION?

### From the User's Perspective

| User Need | How SmartInterview Helps |
|---|---|
| "I want to practise but don't know what questions to expect" | The system generates questions based on the user's resume and target job |
| "I want feedback on how I answer, not just whether the answer is correct" | Multi-signal evaluation covers communication, depth, relevance, and completeness |
| "I want to track my improvement over time" | Performance dashboard shows trends across sessions |
| "I want a voice-based experience like a real interview" | Built-in speech-to-text and text-to-speech |
| "I want to study for my college exams through questions" | Syllabus Mode allows uploading course material |
| "I want a report I can share with a mentor or instructor" | Downloadable PDF performance report |

### What Inconvenience Does It Reduce?

Without SmartInterview, a user would need to:
1. Search for relevant interview questions online.
2. Figure out which topics match their resume and target job.
3. Find someone to ask questions and give feedback.
4. Manually track their own performance across practice sessions.
5. If using ChatGPT, craft prompts each time, manage conversation flow, and remember to ask for evaluation.

SmartInterview combines all of this into a single, automated workflow.

### Will a User Actually Use This, or Will They Just Use ChatGPT?

Honestly, some users will prefer ChatGPT, especially those who are comfortable prompting AI tools and want maximum flexibility. Our application is not for every user.

However, users who want a **structured, repeatable, low-effort** interview practice experience — especially students who may not be experienced with prompt engineering — are more likely to benefit from a dedicated platform. Similarly, institutions (colleges, training centres) that want to provide standardised preparation for all their students would find a structured platform more suitable than asking each student to individually use ChatGPT.

---

## 8. USER CHOICE / USER INITIATION

A valid concern is whether users will voluntarily use this application or whether it only works if someone requires them to use it.

### Different Scenarios Where Users Would Start a Session

1. **Self-motivated practice:** A student with an interview next week voluntarily starts a practice session to prepare. This is similar to how students voluntarily use question banks or mock test apps before exams.

2. **Pre-interview preparation:** A job seeker receives an interview call and wants to practise on relevant topics. They upload the job description and their resume to get a targeted practice session.

3. **College or training institute requirement:** A college placement cell or training programme asks students to complete a certain number of mock interview sessions as part of preparation. The platform provides trackable records for this purpose.

4. **Instructor-guided usage:** A faculty member or trainer recommends the platform to students as a self-study tool, similar to recommending a textbook or online course.

5. **Repeated improvement:** A user who performed poorly in a previous session comes back to practise again, using the feedback from the earlier session to focus on weak areas.

### Why User Initiation Does Not Make the Application Unnecessary

Many useful applications require user initiation — fitness apps, language learning apps, online exam platforms, and coding practice websites all depend on users choosing to start a session. The fact that a user must initiate use does not reduce the application's value. It simply means the application serves users who are motivated to improve, which is exactly the target audience.

---

## 9. EXISTING SYSTEM / CURRENT APPROACH

### How Do Users Currently Prepare for Technical Interviews?

| Method | Description | Limitation |
|---|---|---|
| **Self-study (books/notes)** | Reading textbooks and making notes on technical topics | No interactivity, no feedback, no simulation of interview conditions |
| **Online coding platforms** (LeetCode, HackerRank) | Practising algorithm and data structure problems | Focused only on coding; no verbal questioning, no communication evaluation |
| **Peer mock interviews** | Asking a friend or classmate to conduct a practice interview | Quality depends on the friend's knowledge; inconsistent; scheduling constraints |
| **Professional coaching** | Hiring a career coach or attending interview preparation workshops | Expensive; limited sessions; not personalised to individual profile |
| **YouTube/online tutorials** | Watching mock interview videos and tips | Passive consumption; no active practice or evaluation |
| **General AI chatbots** (ChatGPT, Gemini, etc.) | Asking AI to simulate an interview or evaluate answers | Not structured; requires manual prompt engineering; no resume analysis; no built-in evaluation rubric; no performance tracking |
| **Enterprise platforms** (HireVue, Talview) | AI-based video interviewing tools used by companies for recruitment | Designed for employers, not learners; not freely accessible; lack transparency in scoring |

### Summary of Limitations

The existing approaches are not fundamentally bad — each one provides some value. The problem is that **no single existing solution combines** resume-aware personalisation, adaptive difficulty progression, voice interaction, structured evaluation, and session tracking into one accessible platform for individual learners.

---

## 10. PROPOSED SYSTEM VS EXISTING GENERAL AI

| Aspect | General AI (e.g., ChatGPT) | SmartInterview (Proposed System) |
|---|---|---|
| **Purpose** | General-purpose AI assistant for any task | Specialised mock interview preparation platform |
| **Target Users** | Anyone with any need | Students, job seekers, training institutes |
| **Input** | User-typed prompts | Resume (PDF) + Job Description / Syllabus material |
| **Interaction** | Text-based conversation | Voice-enabled interview with speech-to-text and text-to-speech |
| **Question Generation** | Based on user prompt | Based on resume-JD skill mapping + RAG knowledge base |
| **Difficulty Adaptation** | Only if user requests it | Automatic, based on Bloom's Taxonomy levels |
| **Evaluation** | General feedback if asked | Multi-signal evaluation (5 distinct metrics) |
| **Personalisation** | Depends on user's prompt quality | Automatic — based on uploaded resume and job description |
| **Output** | Conversational text | Structured PDF report + performance dashboard |
| **Consistency** | Varies with prompt wording | Consistent workflow and evaluation criteria |
| **Session Tracking** | Within a single conversation | Across multiple sessions with historical analytics |
| **Use Case** | Open-ended | Focused interview preparation and skill assessment |

> **Note:** This table is not intended to declare a winner. General AI tools are more flexible and capable across a wider range of tasks. The proposed system is more focused and structured for a specific use case.

---

## 11. OBJECTIVES

1. To develop an AI-powered mock interview platform that simulates a realistic, adaptive technical interview experience for students and job seekers.

2. To design a system that automatically maps skills from uploaded resumes and job descriptions and generates interview questions relevant to the overlapping skill set.

3. To implement a structured difficulty progression model based on Bloom's Taxonomy that adjusts question complexity according to the candidate's real-time performance.

4. To integrate Retrieval-Augmented Generation (RAG) using a vector knowledge base to ensure that generated questions are grounded in verified technical concepts.

5. To provide a multi-signal answer evaluation mechanism that assesses responses across multiple dimensions including technical accuracy, completeness, relevance, and concept coverage.

6. To enable voice-based interaction through integrated text-to-speech and speech-to-text capabilities, creating a more natural and realistic interview environment.

7. To generate structured performance reports and maintain historical analytics that allow users to track their improvement over time.

8. To provide an alternative Syllabus Mode that allows students to upload course material and receive interview-style questioning on academic content.

---

## 12. SIGNIFICANCE OF THE PROJECT

### Academic / Research Significance

- Demonstrates the practical application of Bloom's Taxonomy in AI-driven assessment — connecting educational theory with modern AI systems.
- Explores the use of Retrieval-Augmented Generation (RAG) for grounding generative AI outputs in verified domain knowledge.
- Contributes to the growing body of work on AI-assisted education and skill evaluation.
- Addresses research gaps identified in published literature regarding structured difficulty adaptation and multi-signal evaluation.

### User Significance

- Provides students with a free, accessible, and personalised interview preparation tool.
- Reduces dependence on human availability for mock interviews.
- Gives measurable and structured feedback that helps users focus their improvement efforts.
- Allows unlimited practice at any time, at the user's own pace.

### Practical Significance

- Can be adopted by colleges and training institutes as a standardised placement preparation tool.
- Reduces the subjective variation in interview evaluation that occurs with different human interviewers.
- Demonstrates a practical application of combining multiple AI technologies (LLMs, embeddings, speech processing, vector databases) into a cohesive product.

---

## 13. SCOPE

### What the Project Covers

- Resume and job description upload, parsing, and skill extraction.
- Automated skill mapping between resume and job description.
- AI-generated, adaptive technical interview questions.
- Difficulty progression based on Bloom's Taxonomy.
- Voice-based interaction (text-to-speech and speech-to-text).
- Multi-signal answer evaluation.
- PDF performance report generation.
- Historical performance tracking across sessions.
- Syllabus Mode for academic content-based questioning.
- Support for technical domains relevant to computer science and engineering.

### What the Project Does Not Attempt to Solve

- The project does not replace real human interviews. It is a practice tool, not a hiring decision tool.
- It does not evaluate non-verbal communication (body language, eye contact, facial expressions).
- It does not cover behavioural or HR interview questions in the current version.
- It does not guarantee job placement or specific performance improvement.
- It does not support every possible technical domain — it is focused on common computer science and engineering topics.
- It does not perform live coding assessment or evaluate written code.

---

## 14. EXPECTED OUTCOME

- Users will be able to practise technical interviews in a structured, voice-enabled environment.
- The system will generate questions that are personalised to each user's resume and target job description.
- Question difficulty will progressively adapt based on the user's performance during the session.
- Users will receive a detailed evaluation report covering technical accuracy, communication, depth, and other relevant metrics.
- Users who practise multiple sessions will be able to view their performance trends over time.
- Students using Syllabus Mode will be able to test their understanding of uploaded course material through interview-style questioning.
- The overall experience will be more structured and consistent than using a general-purpose AI chatbot for interview practice.

> **Note:** We do not claim specific numerical accuracy or performance improvement percentages, as formal user studies have not been conducted as part of this academic project.

---

## 15. RESEARCH QUESTIONS

1. Can a specialised, purpose-built interview platform provide a more structured and consistent practice experience compared to using a general-purpose AI assistant?

2. Does incorporating Bloom's Taxonomy as a framework for question difficulty progression lead to a more comprehensive assessment of a candidate's cognitive abilities?

3. Can Retrieval-Augmented Generation (RAG) improve the relevance and accuracy of AI-generated interview questions compared to purely generative approaches?

4. Does multi-signal evaluation (using multiple distinct metrics) provide more useful and actionable feedback to users than a single overall score?

5. Can automated resume-to-job-description skill mapping effectively personalise interview content for individual users?

6. Does voice-based interaction create a more realistic interview simulation compared to text-only interfaces?

7. Can historical performance tracking across sessions motivate users to engage in repeated practice and measurable improvement?

> **Note:** These are research questions that naturally arise from the problem domain. Answering them definitively would require formal experimental studies, which are beyond the scope of this academic project. They are presented here as guiding questions for the project's design and as potential directions for future research.

---

## 16. POSSIBLE LIMITATIONS

1. **Dependence on AI model quality:** The quality of generated questions and evaluation depends on the underlying language model. If the model produces inaccurate or irrelevant output, the user experience will be affected.

2. **Speech recognition accuracy:** Voice-based interaction depends on speech-to-text accuracy, which can be affected by accent, background noise, microphone quality, and speaking speed.

3. **Limited domain coverage:** The current version focuses on computer science and engineering domains. Users from other fields may not find relevant content.

4. **No non-verbal assessment:** The system cannot evaluate body language, eye contact, facial expressions, or other non-verbal communication cues that are important in real interviews.

5. **No behavioural/HR interview support:** The current version focuses on technical interviews and does not cover behavioural or situational interview questions.

6. **Knowledge base maintenance:** The RAG knowledge base needs to be periodically updated to remain current with evolving technologies and industry practices.

7. **Internet dependency:** The system requires a stable internet connection for AI model API calls and speech processing.

8. **User motivation required:** Like any self-preparation tool, the system is only useful if the user is motivated to practise. It cannot force engagement.

9. **Cannot fully replicate a real interview:** No simulated environment can perfectly replicate the pressure, social dynamics, and unpredictability of a real human-conducted interview.

10. **Evaluation is AI-based, not human-verified:** The evaluation is generated by an AI model, which may not always align with how a human interviewer would assess the same answer.

---

## 17. CONCLUSION

Technical interview preparation remains a significant challenge for students and job seekers. Current approaches — including self-study, coding platforms, peer practice, and general AI chatbots — each address part of the problem but none provides a complete, integrated solution.

The two base papers reviewed in this document demonstrate that AI-powered interview systems using large language models and speech recognition can effectively simulate realistic interview experiences. The first paper (Wahid et al., 2026) shows that combining resume-aware questioning, voice interaction, and automated evaluation in a single platform addresses critical gaps in the existing landscape. The second paper (Nagarajan et al., 2026) demonstrates that semantic similarity models can significantly improve resume screening accuracy over traditional keyword-based methods, and that autonomous AI interviews can reduce bias and improve consistency.

However, certain gaps remain at the application level — particularly the absence of a formal educational framework for difficulty progression, the lack of grounding questions in verified knowledge bases, limited multi-signal evaluation, and the absence of long-term performance tracking and academic study modes.

Our proposed application, SmartInterview, addresses these gaps by integrating Bloom's Taxonomy for structured difficulty adaptation, Retrieval-Augmented Generation for grounded question generation, multi-signal evaluation for granular feedback, and historical performance analytics for continuous improvement tracking.

We do not claim that this application renders general-purpose AI tools unnecessary or that it solves every aspect of interview preparation. It is a focused, purpose-built tool that provides a structured, consistent, and personalised experience for users who want systematic interview practice. Its value lies in reducing the effort and inconsistency involved in self-directed preparation, and in providing measurable, repeatable assessment that helps users identify and work on their weaknesses.

---

## 18. VIVA / PROJECT REVIEW — LIKELY QUESTIONS AND ANSWERS

### Q1: What is your problem statement?

**A:** Students and job seekers lack access to a structured, personalised, and adaptive mock interview platform that combines resume-aware questioning, voice interaction, multi-dimensional evaluation, and performance tracking in one place. Existing tools are either too generic, too narrow, or too dependent on human availability.

### Q2: Why did you select this problem?

**A:** Interview preparation is something every student faces, but most students either don't practise enough or practise in ways that don't simulate real interviews. We felt there was a practical need for a tool that gives students a realistic, structured practice experience with proper feedback.

### Q3: What is your base paper?

**A:** We have two base papers. The first is "AI Mock Interview: An Intelligent Voice-Driven Interview Simulation System using Gemini AI and Whisper" published in IJERT, March 2026. The second is "Autonomous AI Interview Engine" published in the Indian Journal of Modern Research and Reviews, February 2026.

### Q4: Why did you select these papers?

**A:** Both papers are directly related to our domain — AI-powered interview systems. The first paper covers the learner-facing side (mock interview for students), and the second covers the recruitment-facing side (automated screening and interviewing). Together, they give us a comprehensive understanding of the problem space.

### Q5: What did you learn from the base papers?

**A:** From the first paper, we learned that combining resume parsing, voice interaction, adaptive questioning, and automated evaluation in one platform is a valid and needed approach. From the second paper, we learned that semantic similarity (meaning-based matching) is much better than keyword matching for comparing resumes with job descriptions, and that autonomous AI interviews can provide consistent, unbiased evaluation.

### Q6: What is the research gap?

**A:** The main gaps we identified are: (1) existing systems don't use a formal educational framework like Bloom's Taxonomy to structure difficulty progression; (2) they don't ground questions in a verified knowledge base; (3) their evaluation uses a single overall score rather than multiple specific metrics; (4) they don't support academic/syllabus-based practice; and (5) they don't track performance across multiple sessions.

### Q7: What is the use of your application?

**A:** Our application helps students and job seekers practise for technical interviews in a structured way. It reads their resume, understands the job they're targeting, asks progressively harder questions, evaluates their answers across multiple dimensions, and gives them a detailed report. They can practise multiple times and track their improvement.

### Q8: Why should someone use your application instead of ChatGPT?

**A:** ChatGPT can definitely help with interview practice. The difference is that our application provides a complete, ready-made workflow. The user just uploads their resume and job description, and the system handles everything — skill mapping, question generation, difficulty adjustment, evaluation, and reporting. With ChatGPT, the user would need to set all of this up themselves through careful prompting, and the experience would be different each time. Our application provides consistency, structure, and tracking.

### Q9: Can't ChatGPT already do this?

**A:** ChatGPT can do many individual parts — generate questions, evaluate answers, give feedback. But it doesn't automatically read resumes, map skills to job descriptions, follow Bloom's Taxonomy for difficulty, pull questions from a knowledge base, generate PDF reports, or track performance across sessions. Our application integrates all of these into one structured platform. It's the difference between a general tool and a specialised solution.

### Q10: Who will use your application?

**A:** Primarily college students preparing for campus placements, fresh graduates looking for jobs, and training institutes that want to provide structured preparation for their students. Professionals preparing for role changes could also use it.

### Q11: Will users actually start the application themselves?

**A:** Yes, in many cases. Students who have an upcoming interview are motivated to practise, just like they use mock test apps before exams. Additionally, colleges and training centres can recommend or require students to use the platform as part of their preparation programme.

### Q12: What is new about your project?

**A:** Three things mainly: (1) Using Bloom's Taxonomy to systematically control question difficulty, not just randomly making questions harder. (2) Using a RAG knowledge base to ground questions in verified content instead of relying purely on the language model. (3) Multi-signal evaluation using five distinct metrics instead of one overall score.

### Q13: What are the limitations?

**A:** The main limitations are: it depends on AI model accuracy, speech recognition can be affected by noise and accents, it currently covers only technical interviews (not behavioural/HR), it cannot evaluate body language, and it requires an internet connection. Also, like any practice tool, it depends on the user's motivation to use it.

### Q14: What is the practical benefit?

**A:** Students get a free, accessible, available-anytime mock interview tool that gives them personalised questions and structured feedback. They don't need to find a person to mock-interview them, and they can practise as many times as they want and track their improvement.

### Q15: What is the difference between your project and existing solutions?

**A:** Existing coding platforms (LeetCode, HackerRank) only test coding — not verbal skills. Peer mock interviews depend on human availability. Enterprise platforms (HireVue) are for employers, not students. General AI chatbots require manual setup and don't provide structured evaluation. Our project combines resume-aware personalisation, voice interaction, Bloom's Taxonomy-based difficulty, RAG-grounded questions, multi-metric evaluation, and performance tracking in one platform.

---

## 19. REFERENCES

### Primary References (Base Papers)

[1] A. Wahid, A. Jha, M. Munshi, S. Sonwane, and A. Chakrawarti, "AI Mock Interview: An Intelligent Voice-Driven Interview Simulation System using Gemini AI and Whisper," *International Journal of Engineering Research & Technology (IJERT)*, vol. 15, no. 03, Mar. 2026. ISSN: 2278-0181.

[2] M. K. Nagarajan, A. Kumar, I. V. S. Vignesh, A. Nehal, and M. Musthafa, "Autonomous AI Interview Engine," *Indian Journal of Modern Research and Reviews (Ind. Jr. of Mod. Res. and Rev.)*, vol. 4, no. 2, Feb. 2026.

### Additional References (Cited Within Base Papers)

[3] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings Using Siamese BERT-Networks," in *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing*, 2019.

[4] A. Vaswani et al., "Attention Is All You Need," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30, 2017.

[5] Google DeepMind, "Gemini: A Family of Highly Capable Multimodal Models," Google LLC, Technical Report, 2023.

[6] A. Radford, J. W. Kim, T. Xu, G. Brockman, C. McLeavey, and I. Sutskever, "Robust Speech Recognition via Large-Scale Weak Supervision," in *Proc. Int. Conf. Machine Learning (ICML)*, 2023, pp. 28492-28518.

[7] D. Cer et al., "Universal Sentence Encoder," arXiv preprint arXiv:1803.11175, 2020.

### General References

[8] B. S. Bloom, M. D. Engelhart, E. J. Furst, W. H. Hill, and D. R. Krathwohl, *Taxonomy of Educational Objectives: The Classification of Educational Goals*, Handbook 1: Cognitive Domain, David McKay Company, 1956.

[9] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in *Advances in Neural Information Processing Systems*, 2020.

---

*Document prepared for academic project review purposes. All claims and statements are based on the referenced base papers and the project description. No fabricated statistics or unsupported claims have been included.*
