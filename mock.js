// mock.js – Realistic mock data for VideoQA demo mode

const MOCK_DATA = {
  processVideo: {
    status: "success",
    session_id: "demo-session-001",
    duration: 142.5,
    language: "en",
    transcript: [
      { time: "0:00", speaker: "Speaker 1", text: "Welcome to this tutorial on machine learning fundamentals." },
      { time: "0:08", speaker: "Speaker 1", text: "Today we will explore the core concepts that drive modern AI systems." },
      { time: "0:17", speaker: "Speaker 1", text: "Let's start with supervised learning, where the model learns from labeled data." },
      { time: "0:28", speaker: "Speaker 2", text: "That's a great starting point. Can you explain how the training loop works?" },
      { time: "0:35", speaker: "Speaker 1", text: "Absolutely. In each iteration, the model makes a prediction, we compute the loss, and then we backpropagate the error." },
      { time: "0:50", speaker: "Speaker 1", text: "The optimizer then adjusts the weights to minimize the loss function." },
      { time: "1:02", speaker: "Speaker 2", text: "And what about overfitting? How do we prevent the model from memorizing training data?" },
      { time: "1:12", speaker: "Speaker 1", text: "Great question. We use techniques like dropout, regularization, and data augmentation." },
      { time: "1:24", speaker: "Speaker 1", text: "Cross-validation is also critical to evaluate generalization." },
      { time: "1:38", speaker: "Speaker 1", text: "In conclusion, understanding these fundamentals is essential for building robust ML systems." },
      { time: "1:52", speaker: "Speaker 1", text: "Thank you for watching. In the next video, we will cover deep neural networks in detail." },
      { time: "2:05", speaker: "Speaker 2", text: "Looking forward to it. That was a very clear explanation." },
    ],
    visuals: [
      { time: "0:00", caption: "Title slide: 'Machine Learning Fundamentals'" },
      { time: "0:17", caption: "Diagram showing supervised vs unsupervised learning" },
      { time: "0:35", caption: "Animation of forward pass through a neural network" },
      { time: "0:50", caption: "Graph showing loss decreasing over training epochs" },
      { time: "1:12", caption: "Slide listing regularization techniques: L1, L2, Dropout" },
      { time: "1:38", caption: "Comparison chart of train vs validation accuracy" },
    ]
  },

  ask: (question) => ({
    status: "success",
    question,
    answer: `Based on the transcript and visual frames, the speaker explains this clearly around the middle section of the video.\n\nThe key explanation revolves around the **training loop** and how the model iteratively improves. Specifically, the speaker describes: (1) making a prediction, (2) computing the loss, and (3) backpropagating the error to update weights via an optimizer.\n\nThe visual frames at that point show a neural network animation, which reinforces the audio explanation. The speaker also emphasizes that understanding the loss function is fundamental to training any machine learning model effectively.`,
    confidence: "High – based on transcript excerpt + 3 matching visual frames",
    evidence: {
      transcript_excerpts: [
        "In each iteration, the model makes a prediction, we compute the loss, and then we backpropagate the error.",
        "The optimizer then adjusts the weights to minimize the loss function."
      ],
      visual_captions: [
        "Animation of forward pass through a neural network",
        "Graph showing loss decreasing over training epochs"
      ]
    },
    clip: {
      start: 35,
      end: 55,
      url: null, // will use placeholder
      label: "0:35 – 0:55 – Training Loop Explanation"
    }
  }),

  summarizeVideo: {
    short: "This video is an introductory tutorial on machine learning fundamentals, covering supervised learning, the training loop, loss functions, and techniques to prevent overfitting. The presenter delivers a clear, structured explanation supported by slides and animations.",
    detailed: [
      "Introduction and overview of machine learning fundamentals (0:00–0:17)",
      "Explanation of supervised learning with labeled data and its applications (0:17–0:28)",
      "Detailed walkthrough of the training loop: prediction → loss → backpropagation → weight update (0:35–0:55)",
      "Role of the optimizer in minimizing the loss function during training (0:50–1:02)",
      "Preventing overfitting using dropout, regularization, data augmentation, and cross-validation (1:02–1:38)",
      "Conclusion emphasizing the importance of ML fundamentals and preview of next topic (1:38–2:05)"
    ],
    chapters: [
      { time: "0:00", title: "Introduction" },
      { time: "0:17", title: "Supervised Learning" },
      { time: "0:35", title: "The Training Loop" },
      { time: "1:02", title: "Preventing Overfitting" },
      { time: "1:38", title: "Conclusion & Next Steps" }
    ]
  },

  summarizeTranscript: {
    key_points: [
      "Machine learning models learn from labeled data in supervised learning.",
      "The training loop involves: predict → compute loss → backpropagate → update weights.",
      "Optimizers minimize the loss function to improve model accuracy.",
      "Overfitting is prevented using dropout, regularization, and data augmentation.",
      "Cross-validation is essential for evaluating model generalization.",
      "The video concludes by previewing a future session on deep neural networks."
    ],
    action_items: [
      "Review backpropagation math for deeper understanding.",
      "Experiment with different regularization techniques on a sample dataset.",
      "Watch the follow-up video on deep neural networks."
    ],
    keywords: [
      "Machine Learning", "Supervised Learning", "Training Loop", "Loss Function",
      "Backpropagation", "Optimizer", "Overfitting", "Dropout", "Regularization",
      "Data Augmentation", "Cross-Validation", "Neural Network", "Deep Learning"
    ]
  }
};

// Simulate async delay
function mockDelay(ms = 1200) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
