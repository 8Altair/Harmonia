function StageCircle({
  accent,
  icon,
  index,
  title,
  description,
  controlLabel,
  options,
  value,
  onChange,
  badge,
}) {
  return (
    <article className={`stage-circle stage-circle--${accent}`}>
      <div className="stage-circle__index">{index}</div>
      <div className="stage-circle__surface">
        <div className="stage-circle__icon" aria-hidden="true">
          {icon}
        </div>

        <div className="stage-circle__copy">
          <h3>{title}</h3>
          <p>{description}</p>
        </div>

        {options ? (
          <label className="stage-circle__control">
            <span>{controlLabel}</span>
            <select value={value} onChange={(event) => onChange(event.target.value)}>
              {options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        ) : (
          <div className="stage-circle__badge">
            <span>{controlLabel}</span>
            <strong>{badge}</strong>
          </div>
        )}
      </div>
    </article>
  );
}

export default StageCircle;
