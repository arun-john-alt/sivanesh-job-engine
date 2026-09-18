// Verified company identities; images are bundled locally (no tracking or API keys).
const logos = {
  'RRD':'rrd', 'Accenture':'accenture', 'Nextpower':'nextpower',
  'Flexing It®':'flexing-it', 'MPloyChek':'mploychek',
  'Vestas':'vestas', 'Comcast':'comcast', 'Ford':'ford',
  'Renault Group / RNTBCI':'renault', 'HP':'hp',
  'Buying Simplified':'buying-simplified', 'Capgemini':'capgemini',
  'Gradiant':'gradiant', 'Hitachi Energy':'hitachi-energy',
  'Schneider Electric':'schneider', 'Rockwell Automation':'rockwell',
  'Konecranes':'konecranes', 'TR / Trifast':'trifast',
  'Danish Business Services':'danish', 'ConverSight':'conversight',
  'AgniKul Cosmos':'agnikul'
};
export function companyLogo(company) {
  const key=Object.hasOwn(logos,company)?logos[company]:null;
  return key?`assets/companies/${key}.${['hitachi-energy','rrd'].includes(key)?'svg':'png'}`:'assets/companies/company.svg';
}
