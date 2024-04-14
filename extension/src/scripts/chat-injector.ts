import { getMyHarvardCourseInfo, getMyHarvardRequirements } from '../utils/scraper';
import { performQueryWrapper } from './perform-query';

(async () => {
  const [courses, requirements] = await Promise.all(
    [getMyHarvardCourseInfo(), getMyHarvardRequirements()]
  );
  console.log(courses, requirements);
  const child = document.querySelector('#isSCL_AutoSuggest');
  const callback = () => {
    if (!child) return;
    console.log(child);
    clearInterval(interval);
    const newButton = document.createElement('a');
    newButton.classList.add('HU_SCL_SearchBox');
    newButton.classList.add('bg-primary');
    newButton.textContent = 'Search with GPT';
    newButton.href = '';
    newButton.addEventListener('click', (event) => {
      event.preventDefault();
      performQueryWrapper();
    });
    child?.after(newButton);
  };
  const interval = setInterval(callback, 100);
})();
