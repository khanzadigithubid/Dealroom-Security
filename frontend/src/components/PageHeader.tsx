type Props = {
  title: string;
  description?: string;
  breadcrumb?: React.ReactNode;
  actions?: React.ReactNode;
};

export default function PageHeader({ title, description, breadcrumb, actions }: Props) {
  return (
    <header className="page-head">
      <div className="page-head-text">
        {breadcrumb}
        <h1>{title}</h1>
        {description && <p className="page-head-desc">{description}</p>}
      </div>
      {actions && <div className="page-head-actions">{actions}</div>}
    </header>
  );
}
