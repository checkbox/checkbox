function showHide(what)
{
	var heading = document.getElementById(what);
	var contents = document.getElementById(what + "-contents");
	var headingcontents = heading.innerHTML;
	var newcontents;

	if (contents.style.display != "block")
	{
		newcontents = headingcontents.replace("closed", "open");
		contents.style.display = "block";
	}
	else
	{
		newcontents = headingcontents.replace("open", "closed");
		contents.style.display = "none";
	}
	
	heading.innerHTML = newcontents;
}

function prettyResults()
{
	var results = document.getElementsByName("testResult");
	var graphics = document.getElementsByName("testGraphic");

	for (i=0; i<results.length; i++)
	{
		contents = results[i].innerHTML.trim();
		switch (contents)
		{
			case "untested":
				results[i].innerHTML = "<span style='color: #888'>skipped</span>";
				graphics[i].innerHTML = "<img class='resultimg' src='images/skip.png' />";
				break;
			case "pass":
				results[i].innerHTML = "<span style='color: #0f0;'>PASSED</span>";
				graphics[i].innerHTML = "<img class='resultimg' src='images/pass.png' />";
				break;
			case "fail":
				results[i].innerHTML = "<span style='background-color: #f00'>FAILED</span>";
				graphics[i].innerHTML = "<img class='resultimg' src='images/fail.png' />";
				break;
			case "unsupported":
				results[i].innerHTML = "<span style='color: #888;'>not required on this system</span>";
				break;
		}

	}
}
