const questions = [
  "Have you used drugs other than those required for medical reasons?",
  "Do you abuse more than one drug at a time?",
  "Are you always able to stop using drugs when you want to?",
  "Have you ever had blackouts or flashbacks as a result of drug use?",
  "Do you ever feel bad or guilty about your drug use?",
  "Does your spouse (or parents) ever complain about your involvement with drugs?",
  "Have you neglected your family because of your use of drugs?",
  "Have you engaged in illegal activities in order to obtain drugs?",
  "Have you ever experienced withdrawal symptoms (felt sick) when you stopped taking drugs?",
  "Have you had medical problems as a result of your drug use (e.g. memory loss, hepatitis, convulsions, bleeding)?",
];

const form = document.querySelector("#predict-form");
const questionSelect = document.querySelector("#question");
const responseInput = document.querySelector("#response");
const submitButton = document.querySelector("#submit");
const predictedAnswer = document.querySelector("#predicted-answer");
const confidence = document.querySelector("#confidence");
const needsClarification = document.querySelector("#needs-clarification");
const modelVersion = document.querySelector("#model-version");
const scores = document.querySelector("#scores");
const message = document.querySelector("#message");

questions.forEach((question) => {
  const option = document.createElement("option");
  option.value = question;
  option.textContent = question;
  questionSelect.appendChild(option);
});

function setResult(data) {
  predictedAnswer.textContent = data.predicted_answer;
  confidence.textContent = Number(data.confidence).toFixed(3);
  needsClarification.textContent = data.needs_clarification ? "Yes" : "No";
  modelVersion.textContent = data.model_version;
  scores.textContent = JSON.stringify(data.scores, null, 2);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  submitButton.disabled = true;

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: questionSelect.value,
        response: responseInput.value,
      }),
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    setResult(data);
  } catch (error) {
    message.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});
