// 8-color palette for speaker chips. Cycles by stable label.
const PALETTE = [
  { bg: 'bg-rose-100',   text: 'text-rose-800',   ring: 'ring-rose-300',   dot: 'bg-rose-500' },
  { bg: 'bg-sky-100',    text: 'text-sky-800',    ring: 'ring-sky-300',    dot: 'bg-sky-500' },
  { bg: 'bg-amber-100',  text: 'text-amber-800',  ring: 'ring-amber-300',  dot: 'bg-amber-500' },
  { bg: 'bg-emerald-100',text: 'text-emerald-800',ring: 'ring-emerald-300',dot: 'bg-emerald-500' },
  { bg: 'bg-violet-100', text: 'text-violet-800', ring: 'ring-violet-300', dot: 'bg-violet-500' },
  { bg: 'bg-fuchsia-100',text: 'text-fuchsia-800',ring: 'ring-fuchsia-300',dot: 'bg-fuchsia-500' },
  { bg: 'bg-teal-100',   text: 'text-teal-800',   ring: 'ring-teal-300',   dot: 'bg-teal-500' },
  { bg: 'bg-orange-100', text: 'text-orange-800', ring: 'ring-orange-300', dot: 'bg-orange-500' },
]

function hash(str: string): number {
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = (h * 31 + str.charCodeAt(i)) >>> 0
  }
  return h
}

export function speakerColor(label: string) {
  return PALETTE[hash(label || 'S?') % PALETTE.length]
}
