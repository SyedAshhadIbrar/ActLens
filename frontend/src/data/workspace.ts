import type { LanguageCode } from "../types/api";

export const LANGUAGE_LABELS: Record<LanguageCode, string> = {
  en: "English",
  fr: "French",
  nl: "Dutch",
};

export const PLACEHOLDERS: Record<LanguageCode, { ask: string; check: string }> = {
  en: {
    ask: "Ask anything about the EU AI Act…",
    check: "Ask how your document compares to the EU AI Act…",
  },
  fr: {
    ask: "Posez une question sur le règlement IA de l'UE…",
    check: "Demandez si votre document est conforme au règlement IA…",
  },
  nl: {
    ask: "Stel een vraag over de EU AI Act…",
    check: "Vraag of uw document voldoet aan de EU AI Act…",
  },
};

export const SUGGESTIONS: Record<LanguageCode, string[]> = {
  en: [
    "What are the risk management requirements for high-risk AI systems?",
    "What practices are prohibited under Article 5?",
    "Are we missing human oversight requirements?",
  ],
  fr: [
    "Quelles sont les exigences de gestion des risques pour les systèmes IA à haut risque?",
    "Quelles pratiques sont interdites à l'article 5?",
    "Manquons-nous des exigences de surveillance humaine?",
  ],
  nl: [
    "Wat zijn de risicobeheerseisen voor hoog-risico AI-systemen?",
    "Welke praktijken zijn verboden onder artikel 5?",
    "Missen we vereisten voor menselijk toezicht?",
  ],
};
