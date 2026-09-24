import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function articleBadge(label: string): string {
  const match = label.match(/Art(?:icle|\.)?\s*(\d+)/i);
  if (match) return `ARTICLE ${match[1]}`;
  const recital = label.match(/Recital\s*\(?(\d+)\)?/i);
  if (recital) return `RECITAL ${recital[1]}`;
  const annex = label.match(/Annex\s+([IVXLC\d]+)/i);
  if (annex) return `ANNEX ${annex[1]}`;
  return "PROVISION";
}
