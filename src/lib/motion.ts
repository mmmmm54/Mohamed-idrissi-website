/*
  Mohamed's videos. The list lives in src/data/motion.json; the encoded files in
  public/motion/<id>/ (full.mp4, preview.mp4, poster.webp) come from
  scripts/encode-motion.py. Add a video: add an entry, run the script, done.
*/
import motionData from '../data/motion.json';

export type MotionGroup = 'reels' | 'ads' | 'real-estate';

export interface MotionItem {
  id: string;
  title: string;
  client?: string;
  project?: string;
  group: MotionGroup;
  duration: number;
  width: number;
  height: number;
}

export const motionGroups: { key: MotionGroup; title: string; note: string }[] = [
  { key: 'reels', title: 'Brand reels', note: 'Short vertical films for a brand’s feed.' },
  { key: 'ads', title: 'Ads', note: 'Paid social spots built to stop the scroll and lead to one action.' },
  { key: 'real-estate', title: 'Real estate films', note: 'Location maps, motion graphics and AI-rendered architecture for projects not yet built.' },
];

export const motion = motionData as unknown as MotionItem[];

export const motionFile = (item: MotionItem, file: 'full.mp4' | 'preview.mp4' | 'poster.webp') => `/motion/${item.id}/${file}`;

/* 76.7 → "1:17" */
export const formatDuration = (seconds: number) => {
  const total = Math.round(seconds);
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`;
};

export const motionFor = (project: string) => motion.filter((item) => item.project === project);
