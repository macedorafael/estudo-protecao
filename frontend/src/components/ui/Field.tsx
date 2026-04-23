import React from 'react'
import { Tooltip } from './Tooltip'

interface FieldProps {
  label: string
  tooltip: string
  link?: string
  linkLabel?: string
  energisa?: boolean
  children: React.ReactElement
  unit?: string
  hint?: string
}

export function Field({ label, tooltip, link, linkLabel, energisa, children, unit, hint }: FieldProps) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-1.5">
        <label className="field-label mb-0">{label}</label>
        {energisa && <span className="energisa-badge">ENERGISA</span>}
        {unit && <span className="text-xs text-gray-400">[{unit}]</span>}
        <Tooltip content={tooltip} link={link} linkLabel={linkLabel}>
          <button
            type="button"
            className="ml-auto flex h-4 w-4 items-center justify-center rounded-full bg-gray-200 text-gray-500 text-xs font-bold hover:bg-gray-300 focus:outline-none"
            aria-label={`Ajuda: ${label}`}
          >
            ?
          </button>
        </Tooltip>
      </div>
      {children}
      {hint && <p className="text-xs text-gray-400">{hint}</p>}
    </div>
  )
}
