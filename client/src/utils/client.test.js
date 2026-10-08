import { getObjects, joinPks } from "./client";

describe("joinPks", () => {
	it("joins integer pks with commas", () => {
		expect(joinPks([1, 2, 3])).toBe("1,2,3");
	});

	it("encodes commas and percent signs in string pks", () => {
		expect(joinPks(["a,b", "50%", "c d"])).toBe("a%2Cb,50%25,c%20d");
	});

	it("skips missing pks", () => {
		expect(joinPks([1, undefined, null, 0, ""])).toBe("1,0,");
	});

		it("returns an empty string for no pks", () => {
		expect(joinPks([])).toBe("");
	});
});

describe("getObjects", () => {
	const originalFetch = window.fetch;

	beforeEach(() => {
		window.fetch = jest.fn().mockResolvedValue({
			ok: true,
			json: () => Promise.resolve({ items: [] }),
		});
	});

	afterEach(() => {
		window.fetch = originalFetch;
	});

	const requestedUrl = () =>
		new URL(window.fetch.mock.calls[0][0], "http://localhost");

	it("sends pks and type to the objects view", async () => {
		await getObjects({
			apiBase: "/autocomplete/",
			pks: "1,2",
			type: "app.Model",
		});

		const url = requestedUrl();
		expect(url.pathname).toBe("/autocomplete/objects/");
		expect(url.searchParams.get("pks")).toBe("1,2");
		expect(url.searchParams.get("type")).toBe("app.Model");
	});

	it("keeps joinPks encoding through the query string", async () => {
		await getObjects({
			apiBase: "/autocomplete/",
			pks: joinPks(["a,b", "50%"]),
			type: "app.Model",
		});

		// The view splits on commas, then unquotes each pk.
		expect(requestedUrl().searchParams.get("pks")).toBe("a%2Cb,50%25");
	});
});
