import { getMyHarvardCourseInfo, getMyHarvardRequirements } from '../utils/scraper';

(async () => {
  const [courses, requirements] = await Promise.all(
    [getMyHarvardCourseInfo(), getMyHarvardRequirements()]
  );
  console.log(courses, requirements);
})();
