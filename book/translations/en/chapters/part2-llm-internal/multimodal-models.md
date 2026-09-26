# Multimodal Models: How Information Beyond Text Enters Computation

The earlier LLM story is simple: text becomes tokens, and a Transformer predicts the next token from context. Multimodality does not overturn that story. It extends model inputs and outputs beyond text to images, audio, video, and other forms of information.

Multimodal capability joins three connected questions: how different signals become computable representations; how they combine with text in one inference; and whether a model finally writes text or can also generate images, speech, and video. Answering them separates where seeing an input, understanding a task, and generating a result each come from.

## The Multimodal Map: Connecting Different Signals to One Computation

Text, images, audio, and video have different raw forms: discrete symbols, pixel arrays, time-varying waveforms, and sequences with both visual content and temporal order. They cannot be mixed unchanged in a Transformer; each must first become a representation.

```text
inputs                                                     outputs

text  ─→ tokenizer / text embeddings ──┐               ┌──→ text tokens → text
image ─→ vision encoder ───────────────┤               │
audio ─→ audio encoder ────────────────┼→ core Transformer ─┼──→ audio tokens / speech decoder → speech
video ─→ video encoder ────────────────┤               │
                                       │               └──→ image/video representation and decoder → image/video
                                       └→ interleaved multimodal context
```

Encoders on the left turn raw signals into vectors or tokens. The core model lets those representations influence each other. Output heads or decoders on the right turn computation back into a deliverable form. These are responsibilities, not a claim that every product has the same separate modules.

Thus, “one model supports text, images, audio, and video” usually means their representations can enter one context and be used by one core computation. It does not mean JPEG bytes, waveforms, and text start as one raw token format, nor that a model necessarily generates every modality.

| Component | What it solves | What it does not guarantee by itself |
| --- | --- | --- |
| Input selection and segmentation | Which patches, audio segments, or video frames enter computation | Every detail is retained |
| Modality encoder | Turns pixels, waveforms, or frames into vectors | The representation already corresponds correctly to the question and text |
| Connector and fusion | Lets the core model use those representations | The model has correctly understood the image or sound |
| Output head or decoder | Delivers computation as text, speech, or an image | The result is factual, or an action has been executed |

## How Inputs Enter One Context

A user can interleave information: text, then an image, an audio clip, video, and a further question. After encoding, the core model can abstractly see:

```text
[text tokens] [image representations] [audio representations] [video-frame representations] [later question tokens]
                                               │
                                               ▼
                                  one Transformer context
```

Images are commonly resized and divided into patches before a vision encoder produces a sequence. Audio is segmented in time. Video must preserve both what frames contain and when they happen. Input selection already determines what the model can see: small labels, fleeting events, tone, or ambient sound can be weakened by resizing, sampling, and compression.

Non-text representations also need a connector, projector, or cross-attention interface into the language model. Implementations vary. Some place visual or audio representations as extra tokens and mostly use self-attention; others let text states query modality representations inside model layers. The common purpose is simple: **textual questions and non-textual evidence must influence one another in the same computation.**

There is no single product organization either. An encoder-plus-connector route commonly gives an LLM multimodal context and produces text or a structured request; a unified discrete-token route can process several modalities in one autoregressive sequence; another kind of system has the core model produce conditions or hidden states for specialist image, speech, or video generators. Modular routing, unified fusion, and external tools can coexist. The task, latency, available data, and verifiability should decide among them, rather than any claim that one route is inherently superior.

This is the meaningful sense of unification. What is unified is the later context and task—not necessarily the initial encoder, connector, or architecture for every modality.

## Two Input Paths for a Monitoring Screenshot

A user sends a monitoring-dashboard screenshot and asks, “Which service's latency suddenly increased?” A system does not have to connect the image directly to a multimodal model. It can first use OCR or an image-description tool, then give the recognized text to a text-only LLM.

```text
path one: screenshot → OCR / image description → text → text LLM → answer

path two: screenshot → visual representations ─┐
                                                 ├→ later multimodal computation → answer
          user question → text representations ─┘
```

The first path leaves a visible transcription for auditing and can reuse existing text flows. But it can lose curve shape, color legends, and spatial layout. If OCR returns only “service A, service B, 120 ms,” a text model may not know which curve that number belongs to. The second path can preserve such relations, but may still misread tiny labels, miss regions, or confuse correspondences. Direct image input is not a guarantee of accurate understanding.

## How One Screenshot Becomes a Text Answer

On the path that connects visual representations directly, service labels, curves, color legends, and time axes from the screenshot must participate in computation together with the question.

Service labels, curves, color legends, and time axes become visual representations. “Which service,” “latency,” and “suddenly increased” become text tokens. In the shared context, the Transformer can use the question's relation to determine how legends, curves, and time positions matter. Fused hidden states finally pass through a text output head to predict “service,” “B,” “after,” “14:20,” and further answer tokens.

```text
screenshot → patches → visual representations ─┐
                                                ├→ [visual representations + question tokens] → Transformer → text answer
question   → tokens → text representations ────┘
```

A vision encoder does not independently conclude that service B's latency rose; it provides clues about lines, colors, text, and position. Nor does the LLM simply guess from language ability; it must connect those clues to the question. A tiny legend, occluded curve, or incorrectly used time axis can still produce a fluent wrong answer.

Audio and video follow the same division of responsibilities. A voice assistant can first transcribe speech, generate a text answer, and then speak it with speech synthesis; [Whisper](https://arxiv.org/abs/2212.04356) is one example of audio-to-text recognition. Transcription means the language model sees only the text: if “do not restart” is transcribed as “restart,” later reasoning starts from the wrong premise. Direct audio representations can retain pauses, tone, and ambient sound, but using those clues correctly still depends on the training task and input sampling. Video has the same constraint: if frames are sampled too sparsely, the moment of change may never enter computation.

## Output Tiers: Understanding Is Not Generating

Inputs and outputs are asymmetric. A model that sees images, hears audio, and understands video most commonly still outputs text or structured data; non-text inputs merely condition that answer.

| Capability type | Input | Output | What must be added |
| --- | --- | --- | --- |
| Multimodal understanding | Text, images, often audio and video too | Text or structured results | Non-text representations affect text-token prediction |
| Multimodal dialogue | Interleaved modalities | Text, sometimes speech | A corresponding token or decoding path for speech |
| Any-to-any generation | Interleaved modalities | Text, images, speech, sometimes video | Representation, prediction, and decoding for every target modality |

Generating speech, images, or video needs an output representation and decoding mechanism. One route discretizes modalities into tokens so a core model predicts them like text; [AnyGPT](https://arxiv.org/abs/2402.12226) and [Chameleon](https://arxiv.org/abs/2405.09818) illustrate this. Another lets the core model produce a condition or hidden state for a specialist generator. [Qwen2.5-Omni](https://arxiv.org/abs/2503.20215) illustrates a reasoning core working with a speech-output module.

A product can appear to accept and return text, images, video, and speech while internally using a jointly trained multimodal model or an LLM plus several specialist generators. The key question is which representations enter the core Transformer and which module produces the final output.

## How Training Forms Cross-Modal Capability

Joining encoders, an LLM, and output modules does not automatically create multimodal ability. Training must establish correspondence, generation, and behavior in layers:

```text
paired or interleaved material: image-text, audio-text, video-text, mixed documents
        │
        ▼
learn how content, position, and time correspond across modalities
        │
        ▼
conditional generation material: given inputs, target text or another modality
        │
        ▼
learn which input evidence should produce which output
        │
        ▼
instruction, preference, verification, and safety signals
        │
        ▼
learn how to organize output for a user's task and restrict unwanted behavior
```

Image-text pairs can teach that a picture and a description are related; they do not teach when an anomaly began. Image-plus-question-plus-answer examples teach which visual evidence is relevant to a question and how to state uncertainty. [CLIP](https://arxiv.org/abs/2103.00020) illustrates matching-oriented alignment, while [LLaVA](https://arxiv.org/abs/2304.08485) illustrates visual instruction tuning that connects images and questions to answers.

If a target is an image, speech, or video, training must contain a representation for that target too. A discrete-token route predicts those tokens directly; a specialist-generator route learns its own objective conditioned on the core model. Neither applies text Softmax directly to raw pixels or waveforms.

Large models can jointly pretrain over text, image, audio, and video, then post-train for dialogue and safety. The [Gemini technical report](https://arxiv.org/abs/2312.11805) describes this organization. Joint training is still not enough by itself: training material must contain the needed relations, objectives must reward their correct use, and evaluation must cover mixed inputs.

## Multimodality Does Not Remove External-System Boundaries

When a model says “service B's latency rose after 14:20,” it interprets a supplied screenshot. It has not retrieved live metrics or restarted a service. Further incident handling needs the [LLM–external-world interaction chain](../part3-llm-external/llm-external-interaction.md) for queries, authorization, execution, and feedback.

Even a task that appears to be only “click the restart button on the screen” still has separate steps: recognize the button, propose an action, have an external program execute it, then observe the interface or service state. Identifying the right coordinates does not authorize the operation; a success notice does not prove the service recovered.

Multimodality expands what a model can observe and generate. It does not automatically grant real-time state, factual correctness, or authority to act. In the book's larger map: **encoders determine which signals enter computation, the core model determines how they combine, output modules determine what can be delivered, and external systems determine whether action is executed and verified.**
