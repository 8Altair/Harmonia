function StageCircle({
  accent,
  icon,
  index,
  title,
  description,
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
          <div className="stage-circle__control">
            <select aria-label={title} value={value} onChange={(event) => onChange(event.target.value)}>
              {options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.value === "Detect" ? "Detect language" : option.label}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div className="stage-circle__badge">
            <strong>{badge}</strong>
          </div>
        )}
      </div>
    </article>
  );
}

export default StageCircle;
