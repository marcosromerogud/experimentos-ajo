function buildQaCookie(qaUrl) {
    const url = new URL(
        qaUrl.startsWith("http")
            ? qaUrl
            : `https://dummy.com/${qaUrl.startsWith("?") ? qaUrl : `?${qaUrl}`}`
    );

    const token = url.searchParams.get("at_preview_token");

    const previewIndex = url.searchParams.get("at_preview_index");

    const listedActivitiesOnly =
        url.searchParams.get("at_preview_listed_activities_only") === "true";

    const audienceIds = url.searchParams.get(
        "at_preview_evaluate_as_true_audience_ids"
    );

    const parts = previewIndex.split("_");

    const previewObject = {
        activityIndex: Number(parts[0])
    };

    if (parts.length > 1) {
        previewObject.experienceIndex = Number(parts[1]);
    }

    const qaData = {
        token,
        listedActivitiesOnly,
        previewIndexes: [previewObject]
    };

    if (audienceIds) {
        qaData.evaluateAsTrueAudienceIds =
            audienceIds.split(",");
    }

    return encodeURIComponent(JSON.stringify(qaData));
}

document
    .getElementById("activate")
    .addEventListener("click", async () => {

        const qaLink =
            document.getElementById("qaLink").value;

        const [tab] =
            await chrome.tabs.query({
                active: true,
                currentWindow: true
            });

        const cookieValue =
            buildQaCookie(qaLink);

        await chrome.scripting.executeScript({
            target: {
                tabId: tab.id
            },
            func: (cookieValue) => {

                document.cookie =
                    `at_qa_mode=${cookieValue}; path=/`;

                location.reload();

            },
            args: [cookieValue]
        });
    });

document
    .getElementById("clear")
    .addEventListener("click", async () => {

        const [tab] =
            await chrome.tabs.query({
                active: true,
                currentWindow: true
            });

        await chrome.scripting.executeScript({
            target: {
                tabId: tab.id
            },
            func: () => {

                document.cookie =
                    "at_qa_mode=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/";

                location.reload();

            }
        });
    });
