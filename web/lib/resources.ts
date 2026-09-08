/** Curated learning resources, extracted from the cloned source
 * repositories by a one-off pass and pinned here so the app has no
 * runtime dependency on `external/`.
 *
 * Each link is classified by keywords in its own title and URL — an
 * imperfect but auditable rule, which is why `via` records which repo
 * surfaced it. 232 links across 27 categories; the full
 * unfiltered index is in INTERVIEW_RESOURCES.md.
 */
export interface Resource {
  label: string;
  url: string;
  /** The repository this link was found in. */
  via: string;
}

export const RESOURCES: Record<string, Resource[]> = {
  "agentic_ai": [
    {
      "label": "Agentic AI Systems",
      "url": "https://www.educative.io/courses/agentic-ai-systems",
      "via": "AIMLInterviews"
    },
    {
      "label": "Agentic Design Patterns",
      "url": "https://www.educative.io/courses/agentic-design-patterns",
      "via": "AIMLInterviews"
    },
    {
      "label": "Build AI Agents and Multi-Agent Systems with CrewAI",
      "url": "https://www.educative.io/courses/build-ai-agents-and-multi-agent-systems-with-crewai",
      "via": "AIMLInterviews"
    },
    {
      "label": "Agentic AI Systems",
      "url": "https://github.com/alirezadir/Agentic-AI-Systems",
      "via": "AIMLInterviews"
    },
    {
      "label": "Agentic AI Systems repo",
      "url": "https://github.com/alirezadir/Agentic-AI-Systems.git",
      "via": "AIMLInterviews"
    },
    {
      "label": "Agentic AI Systems interview prep",
      "url": "https://github.com/alirezadir/Agentic-AI-Systems/tree/main/06_interview_prep",
      "via": "AIMLInterviews"
    },
    {
      "label": "Building Effective Agents Cookbook (Anthropic)",
      "url": "https://www.anthropic.com/engineering/building-effective-agents",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "Anthropic Cookbook (Agents patterns)",
      "url": "https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "OpenAI Cookbook (agent orchestration)",
      "url": "https://cookbook.openai.com/examples/orchestrating_agents",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "AutoGen multi-agent design patterns",
      "url": "https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/intro.html",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "The Anatomy of Agentic AI",
      "url": "https://dr-arsanjani.medium.com/the-anatomy-of-agentic-ai-0ae7d243d13c",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "Llamaindex agents workflow basic",
      "url": "https://docs.llamaindex.ai/en/stable/examples/agent/agent_workflow_basic/",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "Dapr Agentic Cloud Ascent Design Pattern",
      "url": "https://github.com/panaversity/learn-agentic-ai/blob/main/comprehensive_guide_daca.md",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "Deeplearning.AI Agents Courses",
      "url": "https://www.deeplearning.ai/courses/?courses_date_desc%5BrefinementList%5D%5Btopic%5D%5B0%5D=Agents&courses_date_desc%5Bpage%5D=2",
      "via": "Agentic-AI-Systems"
    }
  ],
  "behavioral": [
    {
      "label": "Behavioral & Leadership Interview Prep Worksheet in Google Sheets",
      "url": "https://docs.google.com/spreadsheets/d/1W8H2DMzetOt2BxCTmENOgdfBS84Kf_mbXIHLF2-sP-M/edit?gid=244760119#gid=244760119",
      "via": "AIMLInterviews"
    },
    {
      "label": "behavioral interview question bank",
      "url": "https://www.tryexponent.com/questions?type=behavioral",
      "via": "AIMLInterviews"
    },
    {
      "label": "Course: Behavioral Interviews for Engineers",
      "url": "https://www.tryexponent.com/courses/swe-behavioral",
      "via": "AIMLInterviews"
    }
  ],
  "classical_ml": [
    {
      "label": "All about Logistic Regression in one article",
      "url": "https://towardsdatascience.com/logistic-regression-b0af09cdb8ad",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Understanding Logistic Regression step-by-step",
      "url": "https://towardsdatascience.com/understanding-logistic-regression-step-by-step-704a78be7e0a",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Logistic Regression - Short and Clear Explanation - 9 Mins",
      "url": "https://www.youtube.com/watch?v=yIYKR4sgzI8",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Linear Regression vs Logistic Regression",
      "url": "https://www.youtube.com/watch?v=OCwZyYH14uw",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "30 Questions to test a Data Scientist on Logistic Regression",
      "url": "https://www.analyticsvidhya.com/blog/2017/08/skilltest-logistic-regression/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "30 Questions to test a Data Scientist on Linear Regression",
      "url": "https://www.analyticsvidhya.com/blog/2017/07/30-questions-to-test-a-data-scientist-on-linear-regression/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Ridge Regression - Clearly Explained",
      "url": "https://www.youtube.com/watch?v=Q81RR3yKn30",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Lasso Regression - Clearly Explained",
      "url": "https://www.youtube.com/watch?v=NGf0voTMlcs",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Why Random Forest doesn't work well for Time-Series?",
      "url": "https://medium.com/datadriveninvestor/why-wont-time-series-data-and-random-forests-work-very-well-together-3c9f7b271631",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "The Simple Math behind 3 Decision Tree Splitting criterions",
      "url": "https://mlwhiz.com/blog/2019/11/12/dtsplits/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "All about SVMs - Math, Terminology, Intuition, Kernels in one article",
      "url": "https://towardsdatascience.com/support-vector-machines-svm-c9ef22815589",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "25 Questions to test a Data Scientist on SVMs",
      "url": "https://www.analyticsvidhya.com/blog/2017/10/svm-skilltest/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Clustering and Classification in E-Commerce",
      "url": "https://lucidworks.com/post/clustering-classification-supervised-unsupervised-learning-ecommerce/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Classification v/s Regression",
      "url": "https://medium.com/fintechexplained/supervised-machine-learning-regression-vs-classification-18b2f97708de",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "computer_vision": [
    {
      "label": "Understanding text in images and videos",
      "url": "https://ai.facebook.com/blog/rosetta-understanding-text-in-images-and-videos-with-machine-learning/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Protecting people",
      "url": "https://ai.facebook.com/blog/advances-in-content-understanding-self-supervision-to-protect-people/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Object detection",
      "url": "https://viso.ai/deep-learning/object-detection/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Celesca/fraud-transaction-detection",
      "url": "https://github.com/Celesca/fraud-transaction-detection",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "A Brief Overview of Outlier Detection Techniques",
      "url": "https://towardsdatascience.com/a-brief-overview-of-outlier-detection-techniques-1e0b2c19e561",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "deep_learning": [
    {
      "label": "Udacity's deep learning nanodegree",
      "url": "https://www.udacity.com/course/deep-learning-nanodegree--nd101",
      "via": "AIMLInterviews"
    },
    {
      "label": "Coursera's Deep Learning Specialization",
      "url": "https://www.coursera.org/specializations/deep-learning",
      "via": "AIMLInterviews"
    },
    {
      "label": "full question index published by Devinterview",
      "url": "https://devinterview.io/questions/machine-learning-and-data-science/pytorch-interview-questions/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Scaling AI Experiences at Facebook with PyTorch",
      "url": "https://www.youtube.com/watch?v=O8t9xbAajbY",
      "via": "AIMLInterviews"
    },
    {
      "label": "DeepETA: How Uber Predicts Arrival Times Using Deep Learning",
      "url": "https://www.uber.com/blog/deepeta-how-uber-predicts-arrival-times/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Full Stack Deep Learning course",
      "url": "https://fall2019.fullstackdeeplearning.com/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Probability and Statistics in the context of Deep Learning",
      "url": "https://towardsdatascience.com/probability-and-statistics-explained-in-the-context-of-deep-learning-ed1509b2eb3f",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Why Regularization reduces overfitting in Deep Neural Networks",
      "url": "https://www.youtube.com/watch?v=4nqD5TBlOWU",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Pros and Cons of Neural Networks",
      "url": "https://towardsdatascience.com/hype-disadvantages-of-neural-networks-6af04904ba5b",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "When not to use Neural Networks",
      "url": "https://medium.com/datadriveninvestor/when-not-to-use-neural-networks-89fb50622429",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "40 Questions to test a Data Scientist on Deep learning",
      "url": "https://www.analyticsvidhya.com/blog/2017/04/40-questions-test-data-scientist-deep-learning/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "21 Popular Deep Learning Interview Questions",
      "url": "https://www.analyticsvidhya.com/blog/2020/04/comprehensive-popular-deep-learning-interview-questions-answers/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Deep Learning Interview Questions - Edureka",
      "url": "https://www.youtube.com/watch?v=HGXlFG_Rz4E",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Activation Functions in a Neural Network - Explained",
      "url": "https://towardsdatascience.com/activation-functions-neural-networks-1cbd9f8d91d6",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "dsa": [
    {
      "label": "LeetCode",
      "url": "https://leetcode.com/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Grokking the Coding Interview Patterns",
      "url": "https://www.educative.io/courses/grokking-coding-interview",
      "via": "AIMLInterviews"
    },
    {
      "label": "Grokking Dynamic Programming Patterns for Coding Interviews",
      "url": "https://www.educative.io/courses/grokking-dynamic-programming-interview",
      "via": "AIMLInterviews"
    },
    {
      "label": "the algorithm that started google",
      "url": "https://www.youtube.com/watch?v=qxEkY8OScYY",
      "via": "AIMLInterviews"
    },
    {
      "label": "How does Facebook’s advertising targeting algorithm work?",
      "url": "https://quantmar.com/99/How-does-facebooks-advertising-targeting-algorithm-work",
      "via": "AIMLInterviews"
    },
    {
      "label": "Reliable ML at Netflix",
      "url": "https://www.slideshare.net/justinbasilico/making-netflix-machine-learning-algorithms-reliable",
      "via": "AIMLInterviews"
    },
    {
      "label": "r/leetcode: xAI AI Engineer Interview",
      "url": "https://www.reddit.com/r/leetcode/comments/1pjhw1i/xai_ai_engineer_backendinfra_interview_just/",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "r/leetcode: 2026 Interview Prep",
      "url": "https://www.reddit.com/r/leetcode/comments/1q06zz6/2026_interview_prep",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "The New \"AI-Aware\" Coding Interview: How to Prepare in 2026",
      "url": "https://medium.com/@codegrey/the-new-ai-aware-coding-interview-how-to-prepare-in-2026-6a207d94b23a",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "How to Use AI for Coding Interview Prep in 2026",
      "url": "https://medium.com/@binh.builds/how-to-use-ai-for-coding-interview-prep-in-2026-c9016626f26e",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "5 Sampling algorithms every Data Scientist should know",
      "url": "https://mlwhiz.com/blog/2019/07/30/sampling/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "5 Feature Selection Algorithms every Data Scientist should know",
      "url": "https://towardsdatascience.com/the-5-feature-selection-algorithms-every-data-scientist-need-to-know-3a6b566efd2",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "All Learning Algorithms Explained in 14 Minutes",
      "url": "https://www.youtube.com/watch?v=BT6Aw6Q75Yg",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Decision Tree vs. Random Forest – Which Algorithm Should you Use?",
      "url": "https://www.analyticsvidhya.com/blog/2020/05/decision-tree-vs-random-forest-algorithm/",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "evaluation": [
    {
      "label": "penghor315/metric-synthesis-engine",
      "url": "https://github.com/penghor315/metric-synthesis-engine",
      "via": "ai-engineering-field-guide"
    }
  ],
  "llm_genai": [
    {
      "label": "Generative AI Handbook",
      "url": "https://www.educative.io/courses/generative-ai-handbook",
      "via": "AIMLInterviews"
    },
    {
      "label": "LLM Bootcamp",
      "url": "https://www.educative.io/courses/llm-bootcamp",
      "via": "AIMLInterviews"
    },
    {
      "label": "Become an LLM Engineer",
      "url": "https://www.educative.io/path/become-an-llm-engineer",
      "via": "AIMLInterviews"
    },
    {
      "label": "LLMOps",
      "url": "https://www.educative.io/courses/llmops",
      "via": "AIMLInterviews"
    },
    {
      "label": "Grokking the Generative AI System Design",
      "url": "https://www.educative.io/courses/generative-ai-system-design",
      "via": "AIMLInterviews"
    },
    {
      "label": "Instagram explore recommendation",
      "url": "https://about.instagram.com/blog/engineering/designing-a-constrained-exploration-system",
      "via": "AIMLInterviews"
    },
    {
      "label": "Building A Generative AI Platform",
      "url": "https://huyenchip.com/2024/07/25/genai-platform.html#step_1_enhance_context",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "GPT-4 Prompting Guide",
      "url": "https://cookbook.openai.com/examples/gpt4-1_prompting_guide",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "LLM Course",
      "url": "https://github.com/mlabonne/llm-course",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "Awesome LLM Apps",
      "url": "https://github.com/Shubhamsaboo/awesome-llm-apps",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "Intelligent Automation Platform: Empowering Conversational AI and Beyond at Airbnb (Airbnb Tech Blog)",
      "url": "https://airbnb.tech/ai-ml/intelligent-automation-platform-empowering-conversational-ai-and-beyond-at-airbnb/?utm_source=chatgpt.com",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "Hugging Face LLM Leaderboard",
      "url": "https://huggingface.co/spaces/lmarena-ai/chatbot-arena-leaderboard",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "Hugging Face Open LLM Leaderboard",
      "url": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "LLMPerf",
      "url": "https://llmperf.github.io/",
      "via": "Agentic-AI-Systems"
    }
  ],
  "llmops": [
    {
      "label": "Langfuse",
      "url": "https://langfuse.com/",
      "via": "Agentic-AI-Systems"
    }
  ],
  "math_stats": [
    {
      "label": "StatQuest Statistics",
      "url": "https://www.youtube.com/watch?v=qBigTkBLU6g&list=PLblh5JKOoLUK0FLuzwntyYI10UQFUhsY9",
      "via": "AIMLInterviews"
    },
    {
      "label": "Understand the basics of Descriptive Statistics(Really Important for an interview)",
      "url": "https://towardsdatascience.com/understanding-descriptive-statistics-c9c2b0641291",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "40 Question on **probability** for a Data Science Interview",
      "url": "https://www.analyticsvidhya.com/blog/2017/04/40-questions-on-probability-for-all-aspiring-data-scientists/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "40 Statistics Interview Problems and Answers for Data Scientists",
      "url": "https://towardsdatascience.com/40-statistics-interview-problems-and-answers-for-data-scientists-6971a02b7eee",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Probability v/s Likelihood",
      "url": "https://www.youtube.com/watch?v=pYxNSUDSFH4",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "PDF is not a probability",
      "url": "https://towardsdatascience.com/pdf-is-not-a-probability-5a4b8a5d9531",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "The 10 Statistical Techniques Data Scientists Need to Master",
      "url": "https://www.kdnuggets.com/2017/11/10-statistical-techniques-data-scientists-need-master.html",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Crash Course in Applied Linear Algebra",
      "url": "https://youtu.be/wkxgZirbCr4?si=6jk888FeJQYDzIgy",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "12 tips to make most out of Naive Bayes",
      "url": "https://machinelearningmastery.com/better-naive-bayes/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "6 easy steps to learn Naive Bayes",
      "url": "https://www.analyticsvidhya.com/blog/2017/09/naive-bayes-explained/",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "ml_case_study": [
    {
      "label": "Intro to AI at Linkedin",
      "url": "https://engineering.linkedin.com/blog/2018/10/an-introduction-to-ai-at-linkedin",
      "via": "AIMLInterviews"
    },
    {
      "label": "Building The LinkedIn Knowledge Graph",
      "url": "https://engineering.linkedin.com/blog/2016/10/building-the-linkedin-knowledge-graph",
      "via": "AIMLInterviews"
    },
    {
      "label": "Communities AI: Building communities around interests on LinkedIn",
      "url": "https://engineering.linkedin.com/blog/2019/06/building-communities-around-interests",
      "via": "AIMLInterviews"
    },
    {
      "label": "Linkedin's follow feed",
      "url": "https://engineering.linkedin.com/blog/2016/03/followfeed--linkedin-s-feed-made-faster-and-smarter",
      "via": "AIMLInterviews"
    },
    {
      "label": "Exploring Transfer Learning with T5",
      "url": "https://ai.googleblog.com/2020/02/exploring-transfer-learning-with-t5.html",
      "via": "AIMLInterviews"
    },
    {
      "label": "Google Research, 2022 & beyond",
      "url": "https://ai.googleblog.com/2023/01/google-research-2022-beyond-language.html",
      "via": "AIMLInterviews"
    },
    {
      "label": "Large Scale Graph Partitioning",
      "url": "https://engineering.fb.com/core-data/large-scale-graph-partitioning-with-apache-giraph/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Pragmatic Engineer: Tech Hiring Inflection Point",
      "url": "https://blog.pragmaticengineer.com/tech-hiring-is-this-an-inflection-point/",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "How to Succeed in A Data Science Interview",
      "url": "https://blog.pramp.com/how-to-succeed-in-a-data-science-interview-27553ab69d8a",
      "via": "data-science-interviews"
    },
    {
      "label": "Data Science Case Study: Optimizing Product Placement in Retail",
      "url": "https://towardsdatascience.com/data-science-case-study-optimizing-product-placement-in-retail-part-1-2e8b27e16e8d",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "ml_coding": [
    {
      "label": "Mykin-AI: ML Coding Challenge 2024",
      "url": "https://github.com/mykin-ai/ML-coding-challenge-2024",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "Numpy and Pandas Cheatsheet",
      "url": "https://github.com/jessicayung/data-analyst-nd/blob/master/2-intro-to-data-analysis/numpy_pandas_cheatsheet.pdf",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "ml_debugging": [
    {
      "label": "Raunak Yadush: Overcoming ML/AI Interview Failure",
      "url": "https://www.linkedin.com/posts/raunakyadush_i-didnt-pass-my-first-mlai-job-interview-activity-7362445182648152064-ggFs",
      "via": "ai-engineering-field-guide"
    }
  ],
  "ml_system_design": [
    {
      "label": "Grokking the Machine Learning System Design Interview",
      "url": "https://www.educative.io/courses/grokking-the-machine-learning-system-design-interview",
      "via": "AIMLInterviews"
    },
    {
      "label": "Grokking the System Design Interview",
      "url": "https://www.educative.io/courses/grokking-the-system-design-interview",
      "via": "AIMLInterviews"
    },
    {
      "label": "System design primer",
      "url": "https://github.com/donnemartin/system-design-primer",
      "via": "AIMLInterviews"
    },
    {
      "label": "Stanford course on ML system design",
      "url": "https://online.stanford.edu/courses/cs329s-machine-learning-systems-design",
      "via": "AIMLInterviews"
    },
    {
      "label": "Design Gurus: OpenAI System Design",
      "url": "https://www.designgurus.io/blog/openai-system-design-interview-questions",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "How To Answer Any Machine Learning System Design Interview Question",
      "url": "https://towardsdatascience.com/how-to-answer-any-machine-learning-system-design-interview-question-a98656bb7ff0",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "mlops": [
    {
      "label": "Production Level Deep Learning",
      "url": "https://github.com/alirezadir/Production-Level-Deep-Learning",
      "via": "AIMLInterviews"
    },
    {
      "label": "TFX workshop by Robert Crowe",
      "url": "https://conferences.oreilly.com/artificial-intelligence/ai-ca-2019/cdn.oreillystatic.com/en/assets/1/event/298/TFX_%20Production%20ML%20pipelines%20with%20TensorFlow%20Presentation.pdf",
      "via": "AIMLInterviews"
    },
    {
      "label": "Deploy a machine learning model with AWS Elastic Beanstalk",
      "url": "https://medium.com/swlh/deploy-a-machine-learning-model-with-aws-elasticbeanstalk-dfcc47b6043e",
      "via": "AIMLInterviews"
    },
    {
      "label": "Deploying Machine Learning Models as API using AWS",
      "url": "https://medium.com/towards-artificial-intelligence/deploying-machine-learning-models-as-api-using-aws-a25d05518084",
      "via": "AIMLInterviews"
    },
    {
      "label": "Serverless Machine Learning On AWS Lambda",
      "url": "https://medium.com/swlh/how-to-deploy-your-scikit-learn-model-to-aws-44aabb0efcb4",
      "via": "AIMLInterviews"
    },
    {
      "label": "Serving Billions of Personalized News Feeds with AI - Meihong Wang",
      "url": "https://www.youtube.com/watch?v=wcVJZwO_py0&t=80s",
      "via": "AIMLInterviews"
    },
    {
      "label": "Airflow",
      "url": "https://airflow.apache.org/",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "TryExponent: LangChain Deployed Engineer Guide",
      "url": "https://www.tryexponent.com/guides/langchain-deployed-engineer-interview-guide",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "End-to-End multiclass Text Classification pipeline",
      "url": "https://mlwhiz.com/blog/2020/05/24/multitextclass/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "End-to-End multiclass Image Classification pipeline",
      "url": "https://mlwhiz.com/blog/2020/06/06/multiclass_image_classification_pytorch/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Understand the Data Science pipeline",
      "url": "https://towardsdatascience.com/a-beginners-guide-to-the-data-science-pipeline-a4904b2d8ad3",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Take your Machine Learning Models to Production with these 5 simple steps",
      "url": "https://mlwhiz.com/blog/2019/12/25/prod/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "2 way to deploy your ML models",
      "url": "https://towardsdatascience.com/there-are-two-very-different-ways-to-deploy-ml-models-heres-both-ce2e97c7b9b1",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "How to deploy a Keras model as a web app through Flask",
      "url": "https://towardsdatascience.com/deploying-a-keras-deep-learning-model-as-a-web-application-in-p-fc0f2354a7ff",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "multimodal": [
    {
      "label": "StatQuest Machine Learning videos",
      "url": "https://www.youtube.com/watch?v=Gv9_4yMHFhI&list=PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF",
      "via": "AIMLInterviews"
    },
    {
      "label": "Live videos",
      "url": "https://engineering.fb.com/ios/under-the-hood-broadcasting-live-video-to-millions/",
      "via": "AIMLInterviews"
    },
    {
      "label": "WIDeText: A Multimodal Deep Learning Framework",
      "url": "https://medium.com/airbnb-engineering/widetext-a-multimodal-deep-learning-framework-31ce2565880c",
      "via": "AIMLInterviews"
    },
    {
      "label": "CMU lecture on chatbots",
      "url": "http://tts.speech.cs.cmu.edu/courses/11492/slides/chatbots_shrimai.pdf",
      "via": "AIMLInterviews"
    },
    {
      "label": "CMU lecture on spoken dialogue systems",
      "url": "http://tts.speech.cs.cmu.edu/courses/11492/slides/sds_components.pdf",
      "via": "AIMLInterviews"
    },
    {
      "label": "Video",
      "url": "https://www.youtube.com/watch?v=jYYR1fH8k7o",
      "via": "data-science-interviews"
    },
    {
      "label": "Logistic Regression - Understand Everything (Theory + Maths + Coding) in 1 video",
      "url": "https://www.youtube.com/watch?v=VCJdg7YBbAQ",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Lasso, Ridge and Logistic Regression all in one video",
      "url": "https://www.youtube.com/live/vaQxdBEcBzU?si=3judBH9xcRefRwGP",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Linear Regression - Understand Everything (Theory + Maths + Coding) in 1 video",
      "url": "https://www.youtube.com/watch?v=E5RjzSK0fvY",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "KNN Algorithm - Understand Everything (Theory + Maths + Coding) in 1 video",
      "url": "https://www.youtube.com/watch?v=6kZ-OPLNcgE",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Naive Bayes - Understand Everything (Theory + Maths + Coding) in 1 video",
      "url": "https://www.youtube.com/watch?v=vz_xuxYS2PM",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "nlp": [
    {
      "label": "NLP at Facebook",
      "url": "https://www.youtube.com/watch?v=ZcMvffdkSTE",
      "via": "AIMLInterviews"
    },
    {
      "label": "NLP analysis",
      "url": "https://www.kaggle.com/code/greentearus/steam-reviews-nlp-analysis",
      "via": "AIMLInterviews"
    },
    {
      "label": "OpenAI Embeddings",
      "url": "https://platform.openai.com/docs/guides/embeddings",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "Cohere Embeddings",
      "url": "https://docs.cohere.com/docs/embeddings",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "LangChain Embeddings",
      "url": "https://python.langchain.com/docs/modules/data_connection/text_embedding/",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "HyphenAI: Challenge ML NLP NLU",
      "url": "https://github.com/HyphenAI/challenge-ml-nlp-nlu",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "BERT Theory in-depth explanation in one video",
      "url": "https://www.youtube.com/watch?v=90mGPxR2GgY",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "30 Questions to test a Data Scientist on NLP",
      "url": "https://www.analyticsvidhya.com/blog/2017/07/30-questions-test-data-scientist-natural-language-processing-solution-skilltest-nlp/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "11 Most Commonly Asked NLP Interview Questions For Beginners",
      "url": "https://analyticsindiamag.com/11-most-commonly-asked-nlp-interview-questions-for-beginners/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "How to solve 90% of NLP Problems",
      "url": "https://blog.insightdatascience.com/how-to-solve-90-of-nlp-problems-a-step-by-step-guide-fda605278e4e",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Questions asked for NLP Roles at Companies",
      "url": "https://medium.com/modern-nlp/nlp-interview-questions-f062040f32f7",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Understanding BERT in detail - one of the best playlist's to understand the fundamentals and inner workings of",
      "url": "https://www.youtube.com/playlist?list=PLam9sigHPGwOBuH4_4fr-XvDbe5uneaf6",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Word Embeddings, CBoW and Skipgram",
      "url": "https://www.youtube.com/watch?v=Q95SIG4g7SA",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "product_reasoning": [
    {
      "label": "Celesca/ai-product-research-assistant",
      "url": "https://github.com/Celesca/ai-product-research-assistant",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "r/ProductManagement: How Are We Feeling About Take-Home Assessments",
      "url": "https://www.reddit.com/r/ProductManagement/comments/1qhgv57/how_are_we_feeling_about_takehome_assessments_in/",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "Optimizing product prices for an online vendor",
      "url": "https://www.analyticsvidhya.com/blog/2016/07/solving-case-study-optimize-products-price-online-vendor-level-hard/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Large Scale Forecasting for 1000+ products - Nagarro",
      "url": "https://www.youtube.com/watch?v=8jfDBD6xlFM",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "project_deep_dive": [
    {
      "label": "Structuring Machine Learning Projects",
      "url": "https://www.coursera.org/learn/machine-learning-projects",
      "via": "AIMLInterviews"
    },
    {
      "label": "What's your proudest project?",
      "url": "https://www.youtube.com/watch?v=VtsQXHXRmGM",
      "via": "AIMLInterviews"
    },
    {
      "label": "Eduardo-Merino/AI-Engineer-Take-Home-Project",
      "url": "https://github.com/Eduardo-Merino/AI-Engineer-Take-Home-Project",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "Full Stack AI Engineer Interview Questions (Medium)",
      "url": "https://medium.com/@engrmountain/full-stack-ai-engineer-interview-questions-take-home-project-solved-e93927990a5c",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "Advice on building Data Portfolio Projects",
      "url": "https://medium.com/@jasonkgoodman/advice-on-building-data-portfolio-projects-c5f96d8a0627",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "End to End guide for a Machine Learning Project",
      "url": "https://medium.com/fintechexplained/end-to-end-guide-for-machine-learning-project-146c288186dc",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "rag": [
    {
      "label": "Build a RAG System with LangChain",
      "url": "https://www.educative.io/courses/rag-llm",
      "via": "AIMLInterviews"
    },
    {
      "label": "Advanced RAG Techniques",
      "url": "https://www.educative.io/courses/advanced-rag-techniques",
      "via": "AIMLInterviews"
    },
    {
      "label": "Traditional RAG vs. Agentic RAG (NVIDIA)",
      "url": "https://developer.nvidia.com/blog/traditional-rag-vs-agentic-rag-why-ai-agents-need-dynamic-knowledge-to-get-smarter/",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "Uber's Enhanced Agentic RAG",
      "url": "https://www.uber.com/blog/enhanced-agentic-rag/",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "ARAG: Agentic Retrieval Augmented Generation",
      "url": "https://arxiv.org/abs/2506.21931",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "Enhanced Agentic RAG at Uber (Uber Blog)",
      "url": "https://www.uber.com/blog/enhanced-agentic-rag/?utm_source=chatgpt.com",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "AsharAhmad/govgpt-agentic-rag",
      "url": "https://github.com/AsharAhmad/govgpt-agentic-rag",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "HisyWu/rag-ai-engineer-assignment",
      "url": "https://github.com/HisyWu/rag-ai-engineer-assignment",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "KalyanKS-NLP/RAG-Interview-Questions-and-Answers-Hub",
      "url": "https://github.com/KalyanKS-NLP/RAG-Interview-Questions-and-Answers-Hub",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "Dev.to: How I Aced My LLM Interview (RAG Chatbot)",
      "url": "https://dev.to/mrzaizai2k/how-i-aced-my-llm-interview-building-a-rag-chatbot-2p6f",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "Hitendra Patel: RAG from Search Engine to Answer Engine",
      "url": "https://medium.com/@hitendra.patel2986/the-day-i-transformed-my-rag-from-search-engine-to-answer-engine-7629f0fddf07",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "Software Architect Skills: From Solution to AI Architect via RAG",
      "url": "https://www.softwarearchitectskills.com/blog-4-from-solution-architect-to-ai-architect-my-journey-through-rag/",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "Naikkrish: Agentic AI and RAG projects to have",
      "url": "https://www.linkedin.com/posts/naikkrish_2-types-of-projects-that-you-should-have-activity-7342213552465723392-eNyT",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "DataCamp: Top 30 RAG Interview Questions 2026",
      "url": "https://www.datacamp.com/blog/rag-interview-questions",
      "via": "ai-engineering-field-guide"
    }
  ],
  "recsys": [
    {
      "label": "Two tower models for retrieval",
      "url": "https://www.linkedin.com/pulse/personalized-recommendations-iv-two-tower-models-gaurav-chakravorty/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Part 1",
      "url": "https://engineering.linkedin.com/blog/2020/course-recommendations-ai-part-one",
      "via": "AIMLInterviews"
    },
    {
      "label": "Part 2",
      "url": "https://engineering.linkedin.com/blog/2020/course-recommendations-ai-part-two",
      "via": "AIMLInterviews"
    },
    {
      "label": "The AI Behind LinkedIn Recruiter search and recommendation systems",
      "url": "https://engineering.linkedin.com/blog/2019/04/ai-behind-linkedin-recruiter-search-and-recommendation-systems",
      "via": "AIMLInterviews"
    },
    {
      "label": "The YouTube Video Recommendation System",
      "url": "https://www.inf.unibz.it/~ricci/ISR/papers/p293-davidson.pdf",
      "via": "AIMLInterviews"
    },
    {
      "label": "Deep Neural Networks for YouTube Recommendations",
      "url": "https://storage.googleapis.com/pub-tools-public-publication-data/pdf/45530.pdf",
      "via": "AIMLInterviews"
    },
    {
      "label": "Recommending What Video to Watch Next: A Multitask Ranking System",
      "url": "https://daiwk.github.io/assets/youtube-multitask.pdf",
      "via": "AIMLInterviews"
    },
    {
      "label": "Instagram feed ranking",
      "url": "https://www.facebook.com/atscaleevents/videos/1856120757994353/?v=1856120757994353",
      "via": "AIMLInterviews"
    },
    {
      "label": "Recommending items to more than a billion people",
      "url": "https://engineering.fb.com/core-data/recommending-items-to-more-than-a-billion-people/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Social recommendations",
      "url": "https://engineering.fb.com/android/made-in-ny-the-engineering-behind-social-recommendations/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Recommendation at Netflix",
      "url": "https://www.slideshare.net/moustaki/recommending-for-the-world",
      "via": "AIMLInterviews"
    },
    {
      "label": "Past, Present & Future of Recommender Systems: An Industry Perspective",
      "url": "https://www.slideshare.net/justinbasilico/past-present-future-of-recommender-systems-an-industry-perspective",
      "via": "AIMLInterviews"
    },
    {
      "label": "Deep learning for recommender systems",
      "url": "https://www.slideshare.net/moustaki/deep-learning-for-recommender-systems-86752234",
      "via": "AIMLInterviews"
    },
    {
      "label": "CF and content based github",
      "url": "https://github.com/AudreyGermain/Game-Recommendation-System",
      "via": "AIMLInterviews"
    }
  ],
  "research_papers": [
    {
      "label": "Paper",
      "url": "https://www.usenix.org/system/files/conference/atc13/atc13-bronson.pdf",
      "via": "AIMLInterviews"
    },
    {
      "label": "MT for 1000 languages",
      "url": "https://arxiv.org/abs/2205.03983",
      "via": "AIMLInterviews"
    }
  ],
  "responsible_ai": [
    {
      "label": "Bias and Variance - Very clearly explained",
      "url": "https://www.youtube.com/watch?v=EuBBz3bI-aA",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Machine Learning Explanaibility - Crash Course by Kaggle",
      "url": "https://www.kaggle.com/learn/machine-learning-explainability",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Understanding the Bias-Variance Tradeoff",
      "url": "https://towardsdatascience.com/understanding-the-bias-variance-tradeoff-165e6942b229",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "search_ir": [
    {
      "label": "How Google Search works",
      "url": "https://www.google.com/search/howsearchworks/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Photo search",
      "url": "https://engineering.fb.com/ml-applications/under-the-hood-photo-search/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Applying Deep Learning To Airbnb Search",
      "url": "https://dl.acm.org/doi/pdf/10.1145/3292500.3330658",
      "via": "AIMLInterviews"
    },
    {
      "label": "semantic search",
      "url": "https://txt.cohere.ai/what-is-semantic-search/?utm_source=linkedin&utm_medium=paidsocial&utm_campaign=contentpromotion_bloglookalikes",
      "via": "AIMLInterviews"
    },
    {
      "label": "Cutshort: Top AI Engineer Interview Questions 2025",
      "url": "https://cutshort.io/blog/job-search-insights/10-top-ai-engineer-interview-questions-in-2025",
      "via": "ai-engineering-field-guide"
    },
    {
      "label": "Vector-based Methods for Similarity Search (TF-IDF, BM25, SBERT)",
      "url": "https://www.youtube.com/watch?v=ziiF1eFM3_4",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "sql_data": [
    {
      "label": "5 Common SQL Interview Problems for Data Scientists",
      "url": "https://towardsdatascience.com/5-common-sql-interview-problems-for-data-scientists-1bfa02d8bae6",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "46 Questions to test a Data Scientist on SQL",
      "url": "https://www.analyticsvidhya.com/blog/2017/01/46-questions-on-sql-to-test-a-data-science-professional-skilltest-solution/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "30 SQL Interview Questions curated for FAANG by an Ex-Facebook Data Scientist",
      "url": "https://www.nicksingh.com/posts/30-sql-and-database-design-questions-from-real-data-science-interviews",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "SQL Interview Questions",
      "url": "https://365datascience.com/sql-interview-questions/",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "How to ace Data Science Interviews - SQL",
      "url": "https://towardsdatascience.com/how-to-ace-data-science-interviews-sql-b71de212e433",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "3 Must Know SQL Questions to pass your Data Science Interview",
      "url": "https://medium.com/@jayfeng/three-must-know-sql-questions-to-pass-your-data-science-interview-463311c7eaea",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "10 frequently asked SQL Queries in Interviews",
      "url": "https://www.java67.com/2013/04/10-frequently-asked-sql-query-interview-questions-answers-database.html",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Technical Data Science Interview Questions: SQL and Coding",
      "url": "https://hackernoon.com/technical-data-science-interview-questions-sql-and-coding-jv1k32bf",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "How to optimize SQL Queries - Datacamp",
      "url": "https://www.datacamp.com/community/tutorials/sql-tutorial-query",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Ten SQL Concepts You Should Know for Data Science Interviews",
      "url": "https://towardsdatascience.com/ten-sql-concepts-you-should-know-for-data-science-interviews-7acf3e428185",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "transformers": [
    {
      "label": "Illustrated transformer",
      "url": "http://jalammar.github.io/illustrated-transformer/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Vision Transformer (ViT)",
      "url": "https://viso.ai/deep-learning/vision-transformer-vit/",
      "via": "AIMLInterviews"
    },
    {
      "label": "More",
      "url": "https://towardsdatascience.com/detr-end-to-end-object-detection-with-transformers-and-implementation-of-python-8f195015c94d",
      "via": "AIMLInterviews"
    },
    {
      "label": "HuggingFace Sentence Transformers",
      "url": "https://huggingface.co/sentence-transformers",
      "via": "Agentic-AI-Systems"
    },
    {
      "label": "5 Types of Regression and their properties",
      "url": "https://towardsdatascience.com/5-types-of-regression-and-their-properties-c5e1fa12d55e",
      "via": "Data-Science-Interview-Resources"
    },
    {
      "label": "Transformers Theory in-depth explanation in one video",
      "url": "https://www.youtube.com/watch?v=bCz4OMemCcA",
      "via": "Data-Science-Interview-Resources"
    }
  ],
  "general": [
    {
      "label": "Grokking the Machine Learning Interview",
      "url": "https://www.educative.io/courses/grokking-the-machine-learning-interview",
      "via": "AIMLInterviews"
    },
    {
      "label": "My Leet Sheet",
      "url": "https://docs.google.com/spreadsheets/d/1Ry_JLeOp1fw9mSbbp4ji5l3CZNiCwf8Atevpp0YML6E/edit?usp=sharing",
      "via": "AIMLInterviews"
    },
    {
      "label": "Educative.io",
      "url": "https://www.educative.io/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Andrew Ng's Machine Learning Course",
      "url": "https://www.coursera.org/learn/machine-learning",
      "via": "AIMLInterviews"
    },
    {
      "label": "lectures on Youtube",
      "url": "https://www.youtube.com/watch?v=PPLop4L2eGk&list=PLLssT5z_DsK-h9vYZkQkYNWcItqhlRJLN",
      "via": "AIMLInterviews"
    },
    {
      "label": "Machine Learning cheatsheets",
      "url": "https://ml-cheatsheet.readthedocs.io/en/latest/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Chris Albon's ML falshcards",
      "url": "https://machinelearningflashcards.com/",
      "via": "AIMLInterviews"
    },
    {
      "label": "45 ML interview questions",
      "url": "https://www.simplilearn.com/tutorials/machine-learning-tutorial/machine-learning-interview-questions",
      "via": "AIMLInterviews"
    },
    {
      "label": "How to Answer Common Situational Interview Questions",
      "url": "https://www.interviewkickstart.com/career-advice/situational-scenario-based-interview-questions-answers",
      "via": "AIMLInterviews"
    },
    {
      "label": "Why do you want to work here?",
      "url": "https://www.tryexponent.com/questions/1377/why-work-at-google",
      "via": "AIMLInterviews"
    },
    {
      "label": "Tell me about a time you made a mistake.",
      "url": "https://www.tryexponent.com/questions/240/mistake",
      "via": "AIMLInterviews"
    },
    {
      "label": "TorchLeet",
      "url": "https://github.com/Exorust/TorchLeet",
      "via": "AIMLInterviews"
    },
    {
      "label": "Deep-ML",
      "url": "https://www.deep-ml.com/problems",
      "via": "AIMLInterviews"
    },
    {
      "label": "Learning to be Relevant",
      "url": "http://www.shivanirao.info/uploads/3/1/2/8/31287481/cikm-cameryready.v1.pdf",
      "via": "AIMLInterviews"
    },
    {
      "label": "intro to page rank",
      "url": "https://www.youtube.com/watch?v=IKXvSKaI2Ko",
      "via": "AIMLInterviews"
    },
    {
      "label": "Google Cloud Platform Big Data and Machine Learning Fundamentals",
      "url": "https://www.coursera.org/learn/gcp-big-data-ml-fundamentals",
      "via": "AIMLInterviews"
    },
    {
      "label": "AWS Machine Learning Blog",
      "url": "https://aws.amazon.com/blogs/machine-learning/",
      "via": "AIMLInterviews"
    },
    {
      "label": "Machine Learning at Facebook Talk",
      "url": "https://www.youtube.com/watch?v=C4N1IZ1oZGw",
      "via": "AIMLInterviews"
    },
    {
      "label": "Practical Lessons from Predicting Clicks on Ads at Facebook",
      "url": "https://quinonero.net/Publications/predicting-clicks-facebook.pdf",
      "via": "AIMLInterviews"
    },
    {
      "label": "How Facebook News Feed Works",
      "url": "https://techcrunch.com/2016/09/06/ultimate-guide-to-the-news-feed/",
      "via": "AIMLInterviews"
    }
  ]
};

export function resourcesFor(category: string): Resource[] {
  return RESOURCES[category] ?? [];
}
